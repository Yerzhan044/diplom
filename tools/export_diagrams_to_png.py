#!/usr/bin/env python3
"""
Экспортирует все диаграммы Mermaid в PNG формате.
Требует: pip install mmdc (Mermaid CLI)
"""

import os
import subprocess
import sys
from pathlib import Path


def export_diagrams():
    """Экспортирует все диаграммы из docs/diagrams/ в PNG."""

    diagrams_dir = Path("docs/diagrams")
    output_dir = Path("docs/diagrams/images")

    # Создаем папку для изображений
    output_dir.mkdir(parents=True, exist_ok=True)

    print("📊 Экспорт диаграмм в PNG...\n")

    # Находим все .md файлы с диаграммами
    diagram_files = sorted(diagrams_dir.glob("*.md"))

    if not diagram_files:
        print("❌ Диаграммы не найдены в docs/diagrams/")
        return

    for diagram_file in diagram_files:
        output_file = output_dir / f"{diagram_file.stem}.png"

        try:
            # Проверяем установлен ли mmdc
            subprocess.run(["mmdc", "--version"], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("⚠️  Mermaid CLI не установлен")
            print("   Установите: npm install -g @mermaid-js/mermaid-cli")
            print("   Или используйте браузер: docs/diagrams_viewer.html\n")
            return

        print(f"⏳ Экспортирую: {diagram_file.name}...")

        try:
            subprocess.run(
                [
                    "mmdc",
                    "-i",
                    str(diagram_file),
                    "-o",
                    str(output_file),
                    "-w",
                    "1200",
                    "-H",
                    "800",
                ],
                check=True,
                capture_output=True,
            )
            print(f"   ✅ Сохранено: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Ошибка: {e}")
            return

    print(f"\n✅ Экспорт завершен!")
    print(f"   📁 Файлы сохранены в: {output_dir.absolute()}")


def alternative_export():
    """Альтернатива без CLI - использование Chrome headless."""
    print("""
🎨 АЛЬТЕРНАТИВНЫЙ СПОСОБ (без установки CLI):

1. Откройте в браузере:
   open docs/diagrams_viewer.html

2. Для каждой диаграммы:
   - Наведите мышку на диаграмму
   - ПКМ → Export as PNG
   - Изображение скачается в Downloads

3. Или используйте mermaid.live:
   - https://mermaid.live/
   - Скопируйте содержимое диаграммы
   - Export → Download as PNG

4. Сохраните все PNG в папку:
   docs/diagrams/images/
    """)


if __name__ == "__main__":
    try:
        export_diagrams()
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nИспользуйте альтернативный способ:")
        alternative_export()
