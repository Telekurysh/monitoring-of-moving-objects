# Отчёт: нагрузочное тестирование балансировщика (GET/POST)

Этот документ содержит результат и инструкции для воспроизведения нагрузочного тестирования балансировки nginx.

## Подготовка окружения

1. Запустить стек:

```bash
# из корня проекта
docker-compose up --build -d
```

2. Убедиться, что все сервисы подняты: `nginx`, `app_main`, `app_read1`, `app_read2`, `app_mirror`, `db_master`, `db_replica`, `grafana`, `loki`, `promtail`.

3. Доступы:
- Приложение: http://localhost/
- Mirror: http://localhost/mirror/
- Grafana: http://localhost/monitoring/  (admin/admin)

## Команды нагрузочного теста (ApacheBench)

1. GET (балансировка 2:1:1 по /api/v1/...)

```bash
ab -n 1000 -c 50 http://localhost/api/v1/objects
```

3. Просмотреть логи в Grafana (Loki) — панель показывает access/response code/host для каждого инстанса.

## Что нужно проверить

- GET: распределение запросов между `app_main`, `app_read1`, `app_read2` примерно в соотношении 2:1:1; это можно увидеть по логам (promtail -> loki -> grafana) или по метрикам access log (nginx access log + upstream).
- POST/PUT/PATCH/DELETE: все должны приходить только на `app_main`. Это видно по метке upstream в логах и по отсутствию ошибок прав доступа.
- Если тест отправит POST на read-only инстанс (например, обойти nginx и обратиться напрямую), приложение вернёт 403 с сообщением "Write attempted on read-only DB instance".

## Пример результата (вставьте реальные цифры после прогонов)

- GET 1000 запросов, concurrency 50
  - Requests per second: XXX
  - Time per request (mean): YYY ms
  - Distribution:
    - app_main: ~500
    - app_read1: ~250
    - app_read2: ~250

- POST 200 запросов, concurrency 10
  - All routed to app_main; error rate: 0%

## Вывод

Ниже надо приложить графики/скриншоты из Grafana с распределением и временными рядами.
