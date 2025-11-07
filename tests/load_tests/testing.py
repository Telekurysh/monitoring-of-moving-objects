#!/usr/bin/env python3
"""
Система нагрузочного тестирования для базы данных датчиков
Поддерживает PostgreSQL 14 с PostGIS
"""

import asyncio
import asyncpg
import time
import random
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import argparse
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import uuid
import psutil
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Конфигурация тестирования"""
    db_host: str = 'localhost'
    db_port: int = 5432
    db_name: str = 'sensor'
    db_user: str = 'postgres'
    db_password: str = 'password'
    
    # Параметры нагрузки
    num_objects: int = 100
    num_sensors_per_object: int = 2
    num_concurrent_writers: int = 10
    test_duration_seconds: int = 300
    records_per_batch: int = 100
    batch_interval_ms: int = 100
    
    # Параметры зон для тестирования
    num_zones: int = 50
    zone_radius_km: float = 5.0
    
    # Координаты центра тестирования (Хельсинки)
    center_lat: float = 60.1699
    center_lon: float = 24.9384

@dataclass
class TestMetrics:
    """Метрики производительности"""
    timestamp: float
    records_written: int
    write_time_ms: float
    cpu_usage: float
    memory_usage_mb: float
    db_connections: int
    errors: int = 0

class SensorDataGenerator:
    """Генератор данных для датчиков"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.objects = []
        self.sensors = []
        self.zones = []
        
    def generate_realistic_coordinates(self, center_lat: float, center_lon: float, 
                                     max_distance_km: float = 50.0) -> Tuple[float, float]:
        """Генерация реалистичных координат в окрестности центра"""
        # Случайное направление и расстояние
        angle = random.uniform(0, 2 * np.pi)
        distance_km = random.uniform(0, max_distance_km)
        
        # Преобразование в координаты (приблизительно)
        lat_offset = (distance_km / 111.0) * np.cos(angle)  # 111 км ≈ 1 градус широты
        lon_offset = (distance_km / (111.0 * np.cos(np.radians(center_lat)))) * np.sin(angle)
        
        return center_lat + lat_offset, center_lon + lon_offset
    
    def generate_zone_polygon(self, center_lat: float, center_lon: float, 
                            radius_km: float) -> str:
        """Генерация полигона зоны"""
        # Простой круг с 8 точками
        points = []
        for i in range(8):
            angle = (2 * np.pi * i) / 8
            lat_offset = (radius_km / 111.0) * np.cos(angle)
            lon_offset = (radius_km / (111.0 * np.cos(np.radians(center_lat)))) * np.sin(angle)
            
            lat = center_lat + lat_offset  
            lon = center_lon + lon_offset
            points.append(f"{lon} {lat}")
        
        # Замыкаем полигон
        points.append(points[0])
        return f"POLYGON(({', '.join(points)}))"

class DatabaseManager:
    """Менеджер работы с базой данных"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.pool = None
        
    async def create_connection_pool(self):
        """Создание пула соединений"""
        self.pool = await asyncpg.create_pool(
            host=self.config.db_host,
            port=self.config.db_port,
            database=self.config.db_name,
            user=self.config.db_user,
            password=self.config.db_password,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("Пул соединений создан")
    
    async def close_pool(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Пул соединений закрыт")
    
    async def setup_test_data(self, generator: SensorDataGenerator):
        """Настройка тестовых данных"""
        async with self.pool.acquire() as conn:
            # Очистка старых тестовых данных
            await conn.execute("DELETE FROM events WHERE sensor_id IN (SELECT id FROM sensors WHERE object_id IN (SELECT id FROM objects WHERE name LIKE 'TestObj_%'))")
            await conn.execute("DELETE FROM sensors WHERE object_id IN (SELECT id FROM objects WHERE name LIKE 'TestObj_%')")
            await conn.execute("DELETE FROM objects WHERE name LIKE 'TestObj_%'")
            await conn.execute("DELETE FROM zones WHERE name LIKE 'TestZone_%'")
            
            # Создание тестовых объектов
            logger.info(f"Создание {self.config.num_objects} тестовых объектов...")
            for i in range(self.config.num_objects):
                obj_id = await conn.fetchval(
                    "INSERT INTO objects (name, object_type, description) VALUES ($1, $2, $3) RETURNING id",
                    f"TestObj_{i:04d}", "VEHICLE", f"Test vehicle {i}"
                )
                generator.objects.append(obj_id)
                
                # Создание датчиков для объекта
                for j in range(self.config.num_sensors_per_object):
                    lat, lon = generator.generate_realistic_coordinates(
                        self.config.center_lat, self.config.center_lon
                    )
                    sensor_id = await conn.fetchval(
                        """INSERT INTO sensors (object_id, sensor_type, location, latitude, longitude) 
                           VALUES ($1, $2, $3, $4, $5) RETURNING id""",
                        obj_id, "GPS", f"GPS_{j}", lat, lon
                    )
                    generator.sensors.append(sensor_id)
            
            # Создание тестовых зон
            logger.info(f"Создание {self.config.num_zones} тестовых зон...")
            for i in range(self.config.num_zones):
                center_lat, center_lon = generator.generate_realistic_coordinates(
                    self.config.center_lat, self.config.center_lon, 30.0
                )
                polygon_wkt = generator.generate_zone_polygon(
                    center_lat, center_lon, self.config.zone_radius_km
                )
                
                zone_id = await conn.fetchval(
                    """INSERT INTO zones (name, zone_type, coordinates, boundary_polygon, center_point) 
                       VALUES ($1, $2, $3, ST_GeomFromText($4, 4326), ST_SetSRID(ST_MakePoint($5, $6), 4326)) 
                       RETURNING id""",
                    f"TestZone_{i:04d}", "CIRCLE", 
                    json.dumps({"center": {"lat": center_lat, "lon": center_lon}, "radius": self.config.zone_radius_km}),
                    polygon_wkt, center_lon, center_lat
                )
                generator.zones.append(zone_id)
            
            logger.info(f"Создано объектов: {len(generator.objects)}, датчиков: {len(generator.sensors)}, зон: {len(generator.zones)}")

class LoadTester:
    """Основной класс нагрузочного тестирования"""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.db_manager = DatabaseManager(config)
        self.generator = SensorDataGenerator(config)
        self.metrics: List[TestMetrics] = []
        self.is_running = False
        
    async def write_sensor_events_batch(self, sensor_ids: List[str], batch_size: int) -> Tuple[int, float]:
        """Запись батча событий датчиков"""
        start_time = time.time()
        events_written = 0
        
        try:
            async with self.db_manager.pool.acquire() as conn:
                # Подготовка данных для батча
                events_data = []
                current_time = datetime.now()
                
                for _ in range(batch_size):
                    sensor_id = random.choice(sensor_ids)
                    
                    # Генерация реалистичных координат с движением
                    lat, lon = self.generator.generate_realistic_coordinates(
                        self.config.center_lat, self.config.center_lon, 25.0
                    )
                    
                    events_data.append((
                        sensor_id,
                        current_time - timedelta(seconds=random.randint(0, 3600)),
                        lat,
                        lon,
                        random.uniform(0, 120),  # Скорость в км/ч
                        random.choice(['MOVE', 'STOP', 'ZONE_ENTER', 'ZONE_EXIT']),
                        f"Auto-generated event {random.randint(1000, 9999)}"
                    ))
                
                # Массовая вставка
                await conn.executemany(
                    """INSERT INTO events (sensor_id, timestamp, latitude, longitude, speed, event_type, details) 
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    events_data
                )
                events_written = len(events_data)
                
        except Exception as e:
            logger.error(f"Ошибка записи батча: {e}")
            return 0, time.time() - start_time
        
        return events_written, (time.time() - start_time) * 1000
    
    def collect_system_metrics(self) -> Tuple[float, float, int]:
        """Сбор системных метрик"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            memory_used_mb = (memory_info.total - memory_info.available) / 1024 / 1024
            
            # Подсчет соединений PostgreSQL (приблизительно)
            db_connections = len([p for p in psutil.process_iter(['name']) 
                                if p.info['name'] and 'postgres' in p.info['name'].lower()])
            
            return cpu_percent, memory_used_mb, db_connections
        except:
            return 0.0, 0.0, 0
    
    async def worker_thread(self, worker_id: int, sensor_ids: List[str]):
        """Рабочий поток для записи данных"""
        logger.info(f"Запуск воркера {worker_id}")
        total_records = 0
        
        while self.is_running:
            try:
                records_written, write_time = await self.write_sensor_events_batch(
                    sensor_ids, self.config.records_per_batch
                )
                total_records += records_written
                
                # Сбор метрик
                cpu_usage, memory_usage, db_connections = self.collect_system_metrics()
                
                metric = TestMetrics(
                    timestamp=time.time(),
                    records_written=records_written,
                    write_time_ms=write_time,
                    cpu_usage=cpu_usage,
                    memory_usage_mb=memory_usage,
                    db_connections=db_connections
                )
                self.metrics.append(metric)
                
                # Интервал между батчами
                await asyncio.sleep(self.config.batch_interval_ms / 1000.0)
                
            except Exception as e:
                logger.error(f"Ошибка в воркере {worker_id}: {e}")
                error_metric = TestMetrics(
                    timestamp=time.time(),
                    records_written=0,
                    write_time_ms=0,
                    cpu_usage=0,
                    memory_usage_mb=0,
                    db_connections=0,
                    errors=1
                )
                self.metrics.append(error_metric)
                await asyncio.sleep(1)  # Пауза при ошибке
        
        logger.info(f"Воркер {worker_id} завершен. Всего записано: {total_records} записей")
    
    async def run_load_test(self):
        """Запуск нагрузочного тестирования"""
        logger.info("Начало нагрузочного тестирования")
        
        # Инициализация БД
        await self.db_manager.create_connection_pool()
        await self.db_manager.setup_test_data(self.generator)
        
        # Запуск воркеров
        self.is_running = True
        start_time = time.time()
        
        workers = []
        for i in range(self.config.num_concurrent_writers):
            worker = asyncio.create_task(
                self.worker_thread(i, self.generator.sensors)
            )
            workers.append(worker)
        
        # Ожидание завершения теста
        await asyncio.sleep(self.config.test_duration_seconds)
        self.is_running = False
        
        # Ожидание завершения всех воркеров
        await asyncio.gather(*workers, return_exceptions=True)
        
        test_duration = time.time() - start_time
        logger.info(f"Тест завершен за {test_duration:.2f} секунд")
        
        await self.db_manager.close_pool()
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Анализ результатов тестирования"""
        if not self.metrics:
            return {"error": "Нет данных метрик"}
        
        total_records = sum(m.records_written for m in self.metrics)
        total_errors = sum(m.errors for m in self.metrics)
        avg_write_time = np.mean([m.write_time_ms for m in self.metrics if m.write_time_ms > 0])
        max_write_time = max([m.write_time_ms for m in self.metrics if m.write_time_ms > 0], default=0)
        avg_cpu = np.mean([m.cpu_usage for m in self.metrics])
        avg_memory = np.mean([m.memory_usage_mb for m in self.metrics])
        max_db_connections = max([m.db_connections for m in self.metrics], default=0)
        
        # Вычисление пропускной способности
        test_duration = max([m.timestamp for m in self.metrics]) - min([m.timestamp for m in self.metrics])
        throughput_rps = total_records / test_duration if test_duration > 0 else 0
        
        return {
            "total_records": total_records,
            "total_errors": total_errors,
            "test_duration_seconds": test_duration,
            "throughput_records_per_second": throughput_rps,
            "avg_write_time_ms": avg_write_time,
            "max_write_time_ms": max_write_time,
            "avg_cpu_usage_percent": avg_cpu,
            "avg_memory_usage_mb": avg_memory,
            "max_db_connections": max_db_connections,
            "error_rate_percent": (total_errors / len(self.metrics)) * 100 if self.metrics else 0
        }
    
    def generate_performance_graphs(self, results: Dict[str, Any]):
        """Генерация графиков производительности"""
        if not self.metrics:
            logger.warning("Нет данных для построения графиков")
            return
        
        # Подготовка данных
        timestamps = [m.timestamp for m in self.metrics]
        start_time = min(timestamps)
        relative_times = [(t - start_time) for t in timestamps]
        
        write_times = [m.write_time_ms for m in self.metrics]
        cpu_usage = [m.cpu_usage for m in self.metrics]
        memory_usage = [m.memory_usage_mb for m in self.metrics]
        records_written = [m.records_written for m in self.metrics]
        
        # Настройка стиля графиков
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Результаты нагрузочного тестирования PostgreSQL 14 + PostGIS', fontsize=16, fontweight='bold')
        
        # График времени записи
        axes[0, 0].plot(relative_times, write_times, 'b-', alpha=0.7, linewidth=1)
        axes[0, 0].set_title('Время записи батча')
        axes[0, 0].set_xlabel('Время (сек)')
        axes[0, 0].set_ylabel('Время записи (мс)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # График загрузки CPU
        axes[0, 1].plot(relative_times, cpu_usage, 'r-', alpha=0.7, linewidth=1)
        axes[0, 1].set_title('Загрузка CPU')
        axes[0, 1].set_xlabel('Время (сек)')
        axes[0, 1].set_ylabel('CPU (%)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # График использования памяти
        axes[1, 0].plot(relative_times, memory_usage, 'g-', alpha=0.7, linewidth=1)
        axes[1, 0].set_title('Использование памяти')
        axes[1, 0].set_xlabel('Время (сек)')
        axes[1, 0].set_ylabel('Память (МБ)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # График пропускной способности (записей в батче)
        axes[1, 1].bar(range(len(records_written)), records_written, alpha=0.7, color='orange')
        axes[1, 1].set_title('Записи в батче')
        axes[1, 1].set_xlabel('Номер батча')
        axes[1, 1].set_ylabel('Количество записей')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Сохранение графика
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_results_{timestamp_str}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        logger.info(f"График сохранен: {filename}")
        
        plt.show()
        
        # Дополнительный график: распределение времени записи
        plt.figure(figsize=(10, 6))
        plt.hist(write_times, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Распределение времени записи батчей')
        plt.xlabel('Время записи (мс)')
        plt.ylabel('Частота')
        plt.grid(True, alpha=0.3)
        
        # Статистики на графике
        plt.axvline(np.mean(write_times), color='red', linestyle='--', 
                   label=f'Среднее: {np.mean(write_times):.2f} мс')
        plt.axvline(np.median(write_times), color='green', linestyle='--', 
                   label=f'Медиана: {np.median(write_times):.2f} мс')
        plt.legend()
        
        hist_filename = f"write_time_distribution_{timestamp_str}.png"
        plt.savefig(hist_filename, dpi=300, bbox_inches='tight')
        logger.info(f"Гистограмма сохранена: {hist_filename}")
        
        plt.show()

BATCH_SIZES_TO_TEST = [10, 30, 50, 80, 100]

async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Нагрузочное тестирование базы данных датчиков')
    parser.add_argument('--host', default='localhost', help='Хост БД')
    parser.add_argument('--port', type=int, default=5432, help='Порт БД')
    parser.add_argument('--database', default='sensor', help='Имя БД')
    parser.add_argument('--user', default='postgres', help='Пользователь БД')
    parser.add_argument('--password', default='password', help='Пароль БД')
    parser.add_argument('--objects', type=int, default=100, help='Количество объектов')
    parser.add_argument('--sensors', type=int, default=2, help='Количество датчиков на объект')
    parser.add_argument('--workers', type=int, default=10, help='Количество параллельных воркеров')
    parser.add_argument('--duration', type=int, default=300, help='Длительность теста (сек)')
    parser.add_argument('--batch-size', type=int, default=100, help='Размер батча записей')
    parser.add_argument('--batch-interval', type=int, default=100, help='Интервал между батчами (мс)')
    parser.add_argument('--zones', type=int, default=50, help='Количество зон')
    parser.add_argument('--compare-batch-sizes', action='store_true', help='Сравнить разные размеры батча')
    
    args = parser.parse_args()
    
    # Конфигурация теста
    config = TestConfig(
        db_host=args.host,
        db_port=args.port,
        db_name=args.database,
        db_user=args.user,
        db_password=args.password,
        num_objects=args.objects,
        num_sensors_per_object=args.sensors,
        num_concurrent_writers=args.workers,
        test_duration_seconds=args.duration,
        records_per_batch=args.batch_size,
        batch_interval_ms=args.batch_interval,
        num_zones=args.zones
    )
    
    # Если выбран режим сравнения размеров батча
    if getattr(args, "compare_batch_sizes", False):
        all_results = {}
        all_metrics = {}
        for batch_size in BATCH_SIZES_TO_TEST:
            logger.info(f"\n=== Тестирование с batch_size={batch_size} ===")
            config.records_per_batch = batch_size
            tester = LoadTester(config)
            results = await tester.run_load_test()
            all_results[batch_size] = results
            all_metrics[batch_size] = tester.metrics
        # Сравнительный график
        plot_batch_size_comparison(all_metrics, all_results)
        # Вывод результатов
        logger.info("\n=== Сравнительные результаты ===")
        for batch_size in BATCH_SIZES_TO_TEST:
            logger.info(f"\nBatch size: {batch_size}")
            for key, value in all_results[batch_size].items():
                if isinstance(value, float):
                    logger.info(f"{key}: {value:.2f}")
                else:
                    logger.info(f"{key}: {value}")
        return

    # Создание и запуск тестера
    tester = LoadTester(config)
    
    try:
        logger.info("Начало нагрузочного тестирования...")
        logger.info(f"Конфигурация: {asdict(config)}")
        
        results = await tester.run_load_test()
        
        # Вывод результатов
        logger.info("=" * 60)
        logger.info("РЕЗУЛЬТАТЫ НАГРУЗОЧНОГО ТЕСТИРОВАНИЯ")
        logger.info("=" * 60)
        for key, value in results.items():
            if isinstance(value, float):
                logger.info(f"{key}: {value:.2f}")
            else:
                logger.info(f"{key}: {value}")
        logger.info("=" * 60)
        
        # Построение графиков
        tester.generate_performance_graphs(results)
        
        # Рекомендации
        logger.info("\nРЕКОМЕНДАЦИИ:")
        if results.get('throughput_records_per_second', 0) < 100:
            logger.info("- Низкая пропускная способность. Рассмотрите увеличение размера батча или оптимизацию индексов")
        if results.get('avg_write_time_ms', 0) > 1000:
            logger.info("- Высокое время записи. Проверьте конфигурацию PostgreSQL и дисковую подсистему")
        if results.get('error_rate_percent', 0) > 5:
            logger.info("- Высокий процент ошибок. Проверьте лимиты соединений и таймауты")
        if results.get('avg_cpu_usage_percent', 0) > 80:
            logger.info("- Высокая загрузка CPU. Рассмотрите масштабирование или оптимизацию запросов")
            
    except Exception as e:
        logger.error(f"Ошибка выполнения теста: {e}")
        raise

def plot_batch_size_comparison(all_metrics, all_results):
    """Построение сравнительных графиков по разным размерам батча"""
    import matplotlib.pyplot as plt
    import numpy as np

    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Сравнение разных batch_size', fontsize=16, fontweight='bold')

    colors = ['b', 'g', 'r', 'c', 'm']
    for idx, batch_size in enumerate(sorted(all_metrics.keys())):
        metrics = all_metrics[batch_size]
        if not metrics:
            continue
        timestamps = [m.timestamp for m in metrics]
        start_time = min(timestamps)
        relative_times = [(t - start_time) for t in timestamps]
        write_times = [m.write_time_ms for m in metrics]
        cpu_usage = [m.cpu_usage for m in metrics]
        memory_usage = [m.memory_usage_mb for m in metrics]
        records_written = [m.records_written for m in metrics]

        label = f'batch={batch_size}'
        color = colors[idx % len(colors)]

        axes[0, 0].plot(relative_times, write_times, label=label, color=color, alpha=0.7)
        axes[0, 1].plot(relative_times, cpu_usage, label=label, color=color, alpha=0.7)
        axes[1, 0].plot(relative_times, memory_usage, label=label, color=color, alpha=0.7)
        axes[1, 1].plot(relative_times, records_written, label=label, color=color, alpha=0.7)

    axes[0, 0].set_title('Время записи батча')
    axes[0, 0].set_xlabel('Время (сек)')
    axes[0, 0].set_ylabel('Время записи (мс)')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()

    axes[0, 1].set_title('Загрузка CPU')
    axes[0, 1].set_xlabel('Время (сек)')
    axes[0, 1].set_ylabel('CPU (%)')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()

    axes[1, 0].set_title('Использование памяти')
    axes[1, 0].set_xlabel('Время (сек)')
    axes[1, 0].set_ylabel('Память (МБ)')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()

    axes[1, 1].set_title('Записи в батче')
    axes[1, 1].set_xlabel('Номер батча')
    axes[1, 1].set_ylabel('Количество записей')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()

    plt.tight_layout()
    plt.show()

    # --- Дополнительные сравнительные графики по batch size ---
    batch_sizes = sorted(all_results.keys())
    throughputs = [all_results[bs].get('throughput_records_per_second', 0) for bs in batch_sizes]
    avg_write_times = [all_results[bs].get('avg_write_time_ms', 0) for bs in batch_sizes]
    error_rates = [all_results[bs].get('error_rate_percent', 0) for bs in batch_sizes]

    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
    fig2.suptitle('Сравнение batch size: итоговые метрики', fontsize=15, fontweight='bold')

    # Пропускная способность
    axes2[0].plot(batch_sizes, throughputs, marker='o')
    axes2[0].set_title('Пропускная способность')
    axes2[0].set_xlabel('Batch size')
    axes2[0].set_ylabel('Записей/сек')
    axes2[0].grid(True, alpha=0.3)

    # Среднее время записи
    axes2[1].plot(batch_sizes, avg_write_times, marker='o', color='orange')
    axes2[1].set_title('Среднее время записи батча')
    axes2[1].set_xlabel('Batch size')
    axes2[1].set_ylabel('Время (мс)')
    axes2[1].grid(True, alpha=0.3)

    # Error rate
    axes2[2].plot(batch_sizes, error_rates, marker='o', color='red')
    axes2[2].set_title('Error rate')
    axes2[2].set_xlabel('Batch size')
    axes2[2].set_ylabel('Ошибки (%)')
    axes2[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())