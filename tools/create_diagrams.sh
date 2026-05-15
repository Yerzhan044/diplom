#!/bin/bash
# Быстрый скрипт для создания диаграмм через Mermaid CLI

echo "📊 Создание PNG диаграмм из Mermaid файлов..."
echo ""

# Проверяем mmdc
if ! command -v mmdc &> /dev/null; then
    echo "Установка Mermaid CLI глобально..."
    sudo npm install -g @mermaid-js/mermaid-cli
fi

# Создаем папку для изображений
mkdir -p docs/diagrams/images

# Экспортируем каждую диаграмму
for file in docs/diagrams/*.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file" .md)
        output="docs/diagrams/images/${filename}.png"
        
        echo "⏳ Обработка: $filename..."
        mmdc -i "$file" -o "$output" -w 1400 -H 900 --scale 2
        echo "✓ Сохранено: $output"
    fi
done

echo ""
echo "✅ Все диаграммы созданы!"
echo "📂 Папка: docs/diagrams/images/"
echo ""
echo "Откройте диаграммы:"
ls -lh docs/diagrams/images/
