#!/usr/bin/env bash

#   --mode MODE       : один из serial|xdist_auto|xdist_4|xdist_loadscope|all (по умолчанию all)
#   --tests PATH      : путь к тестам/папке/файлу (по умолчанию tests/)
#   --open / --no-open: открывать ли allure-report в конце (по умолчанию --open)
#   -h | --help       : показать помощь
#
# Примеры:
#   bash tests.sh                 # запустит все режимы, объединит результаты и откроет отчет
#   bash tests.sh --mode serial   # только последовательный прогон
#   bash tests.sh --mode xdist_4 --tests tests/ -no-open

PIDS_FILE="./tests/_pids.log"
OPEN_REPORT=true
MODE="all"
TESTS_PATH="tests/"
RANDOMIZE=false
RANDOM_SEED=""

print_help() {
    cat <<EOF
Использование:
  $(basename "$0") [--mode MODE] [--tests PATH] [--open|--no-open] [-h|--help]

Опции:
  --mode MODE       serial | xdist_auto | xdist_4 | xdist_loadscope | all
  --tests PATH      путь к тестам (файл или папка). По умолчанию: ${TESTS_PATH}
  --open / --no-open  открыть итоговый Allure-отчёт (по умолчанию --open)
  -h, --help        показать это сообщение

Примеры:
  bash tests.sh
  bash tests.sh --mode serial --tests tests/test_zone_service.py
  bash tests.sh --mode xdist_4 --tests tests/ --no-open

Если вы хотите использовать xdist-режимы, установите плагин:
  poetry add pytest-xdist
или
  pip install pytest-xdist
EOF
}

has_xdist() {
    if poetry run pytest --version 2>/dev/null | grep -qi 'xdist'; then
        return 0
    fi

    if poetry run python - <<'PY' 2>/dev/null
import importlib.util, sys
sys.exit(0 if importlib.util.find_spec("xdist") is not None else 1)
PY
    then
        return 0
    fi

    if poetry show pytest-xdist >/dev/null 2>&1; then
        return 0
    fi

    return 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="$2"; shift 2;;
        --tests)
            TESTS_PATH="$2"; shift 2;;
        --open)
            OPEN_REPORT=true; shift;;
        --no-open)
            OPEN_REPORT=false; shift;;
        --randomize)
            RANDOMIZE=true; shift;;
        --seed)
            RANDOM_SEED="$2"; shift 2;;
        -h|--help)
            print_help; exit 0;;
        *)
            echo "Неизвестный аргумент: $1"; print_help; exit 1;;
    esac
done

run_and_report() {
    MODE_DESC="$1"
    MODE_SLUG="$2"
    shift 2
    PYTEST_ARGS=("$@")

    # если включена рандомизация — добавляем seed (генерируем, если не указан)
    if [ "${RANDOMIZE}" = true ]; then
        if [ -z "${RANDOM_SEED}" ]; then
            # сгенерировать 32‑битный случайный seed
            RANDOM_SEED=$(od -An -N4 -tu4 /dev/urandom | tr -d ' ')
        fi
        echo "Используется random seed: ${RANDOM_SEED}"
        PYTEST_ARGS+=("--randomly-seed" "${RANDOM_SEED}")
    fi

    echo
    echo "=== Запуск режима: $MODE_DESC ==="

    MODE_DIR="./allure-results/${MODE_SLUG}"
    rm -rf "$MODE_DIR"
    mkdir -p "$MODE_DIR"

    # Метаданные для Allure, чтобы видно было режим прогона
    cat > "${MODE_DIR}/executor.json" <<EOF
{"name":"${MODE_DESC}","type":"manual"}
EOF
    echo "mode=${MODE_DESC}" > "${MODE_DIR}/environment.properties"

    # Добавляем категории для лучшей организации
    cat > "${MODE_DIR}/categories.json" <<EOF
[
  {
    "name": "Zone Service Tests",
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  },
  {
    "name": "User Service Tests", 
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  },
  {
    "name": "Sensor Service Tests",
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  },
  {
    "name": "Route Service Tests",
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  },
  {
    "name": "Object Service Tests",
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  },
  {
    "name": "Event Service Tests", 
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  },
  {
    "name": "Alert Service Tests",
    "matchedStatuses": ["passed", "failed", "broken", "skipped"]
  }
]
EOF


    if [ -f "$PIDS_FILE" ]; then
        rm -f "$PIDS_FILE"
    fi

    echo "pytest ${PYTEST_ARGS[*]} --alluredir=${MODE_DIR}"
    poetry run pytest "${PYTEST_ARGS[@]}" --alluredir="${MODE_DIR}" -q
    sleep 0.5

    if [ -f "$PIDS_FILE" ]; then
        cp "$PIDS_FILE" "${MODE_DIR}/pids.log"
    fi

    if [ -f "${MODE_DIR}/pids.log" ]; then
        echo
        echo "Содержимое ${MODE_DIR}/pids.log:"
        cat "${MODE_DIR}/pids.log"
        echo
        echo "Статистика по PID (PID - количество записей):"
        awk '{print $1}' "${MODE_DIR}/pids.log" | sort | uniq -c | awk '{print $2" - "$1" записи"}'
        echo "Уникальных PID: $(awk '{print $1}' "${MODE_DIR}/pids.log" | sort -u | wc -l)"
        echo "Уникальных worker-id: $(awk '{print $2}' "${MODE_DIR}/pids.log" | sort -u | wc -l)"
    else
        echo "Файл ${MODE_DIR}/pids.log не найден — тесты не писали PID в этом прогоне."
    fi

    echo "=== Конец режима: $MODE_DESC ==="
    echo
}

declare -a TO_RUN
if [[ "$MODE" == "all" ]]; then
    TO_RUN=( "serial" "xdist_auto" "xdist_4" "xdist_loadscope" )
else
    TO_RUN=( "$MODE" )
fi

if ! has_xdist; then
    SKIP_XDIST=()
    NEW_TO_RUN=()
    for m in "${TO_RUN[@]}"; do
        case "$m" in
            xdist_auto|xdist_4|xdist_loadscope)
                SKIP_XDIST+=("$m")
                ;;
            *)
                NEW_TO_RUN+=("$m")
                ;;
        esac
    done

    if [[ ${#SKIP_XDIST[@]} -gt 0 ]]; then
        if [[ ${#NEW_TO_RUN[@]} -eq 0 ]]; then
            echo "Ошибка: pytest-xdist не установлен, но запрошен xdist-режим (${SKIP_XDIST[*]})."
            echo "Установите плагин: poetry add pytest-xdist  (или pip install pytest-xdist)"
            exit 3
        fi
        echo "Внимание: pytest-xdist не найден — пропускаем xdist-режимы: ${SKIP_XDIST[*]}"
        echo "Чтобы включить xdist-режимы, установите плагин: poetry add pytest-xdist"
        TO_RUN=("${NEW_TO_RUN[@]}")
    fi
fi

# Проверка валидности режимов и маппинг на pytest-аргументы
for m in "${TO_RUN[@]}"; do
    case "$m" in
        serial)
            run_and_report "serial (no xdist)" "serial" "${TESTS_PATH}" -v
            ;;
        xdist_auto)
            run_and_report "xdist -n auto (параллельно по CPU)" "xdist_auto" -n auto "${TESTS_PATH}" -v
            ;;
        xdist_4)
            run_and_report "xdist -n 4 (4 процесса)" "xdist_4" -n 4 "${TESTS_PATH}" -v
            ;;
        xdist_loadscope)
            run_and_report "xdist --dist=loadscope" "xdist_loadscope" -n auto --dist=loadscope "${TESTS_PATH}" -v
            ;;
        *)
            echo "Неизвестный режим: $m"
            echo "Допустимые: serial, xdist_auto, xdist_4, xdist_loadscope, all"
            exit 2
            ;;
    esac
done

# Собираем результаты в один allure-отчет
echo "Собираем все результаты в allure-report/ ..."
rm -rf allure-report
poetry run allure generate --clean --report-dir allure-report allure-results/

if [ "$OPEN_REPORT" = true ]; then
    echo "Открываем allure-report ..."
    poetry run allure open allure-report/
fi