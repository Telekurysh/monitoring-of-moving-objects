#!/usr/bin/env bash
# Simple checker to hit GET endpoint multiple times and show distribution of X-Instance header
set -euo pipefail
COUNT=${1:-200}
URL=${2:-http://localhost/api/v1/objects}

# Временный файл для хранения результатов
TMPFILE=$(mktemp)

# Собираем данные
for i in $(seq 1 $COUNT); do
  # Получаем заголовки и сохраняем во временный файл
  headers=$(curl -s -I $URL)
  
  # Извлекаем значение X-Instance
  inst=$(echo "$headers" | awk -F": " '/^[Xx]-[Ii]nstance/ {print $2}' | tr -d '\r')
  
  if [ -z "$inst" ]; then 
    inst="unknown"
  fi
  
  echo "$inst" >> "$TMPFILE"
done

# Подсчитываем распределение
echo "Distribution of X-Instance headers:"
sort "$TMPFILE" | uniq -c | sort -nr

# Удаляем временный файл
rm -f "$TMPFILE"