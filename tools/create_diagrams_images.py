#!/usr/bin/env python3
"""
Скрипт для создания PNG изображений из Mermaid диаграмм.
Автоматически устанавливает зависимости и экспортирует все диаграммы.
"""

import os
import subprocess
import sys
from pathlib import Path
import json


class DiagramExporter:
    """Экспортирует диаграммы Mermaid в PNG."""

    def __init__(self):
        self.diagrams_dir = Path("docs/diagrams")
        self.output_dir = Path("docs/diagrams/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_dependencies(self):
        """Проверяет установлены ли необходимые инструменты."""
        print("🔍 Проверка зависимостей...\n")

        # Проверяем Node.js
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            print(f"✓ Node.js: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Node.js не установлен")
            print("   Установите: https://nodejs.org/")
            return False

        # Проверяем npm
        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True
            )
            print(f"✓ npm: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ npm не установлен")
            return False

        return True

    def install_mermaid_cli(self):
        """Установляет Mermaid CLI."""
        print("\n📦 Установка Mermaid CLI...\n")

        try:
            # Проверяем установлена ли mmdc
            subprocess.run(["mmdc", "--version"], capture_output=True, check=True)
            print("✓ Mermaid CLI уже установлен")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        print("Установка @mermaid-js/mermaid-cli...")
        try:
            subprocess.run(
                ["npm", "install", "-g", "@mermaid-js/mermaid-cli"],
                check=True,
                capture_output=True,
            )
            print("✓ Mermaid CLI успешно установлен\n")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки: {e}")
            print("\nАльтернатива: установите вручную")
            print("  npm install -g @mermaid-js/mermaid-cli")
            return False

    def export_diagrams(self):
        """Экспортирует все диаграммы в PNG."""
        print("🎨 Экспорт диаграмм в PNG...\n")

        diagram_files = sorted(self.diagrams_dir.glob("*.md"))

        if not diagram_files:
            print(f"❌ Диаграммы не найдены в {self.diagrams_dir}")
            return False

        success_count = 0

        for diagram_file in diagram_files:
            output_file = self.output_dir / f"{diagram_file.stem}.png"

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
                        "1400",
                        "-H",
                        "900",
                        "--scale",
                        "2",
                    ],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )

                print(f"   ✓ {output_file.name}\n")
                success_count += 1

            except subprocess.TimeoutExpired:
                print(f"   ⏱️  Timeout при обработке {diagram_file.name}\n")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Ошибка: {e.stderr.decode() if e.stderr else e}\n")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}\n")

        return success_count > 0

    def create_index_html(self):
        """Создает HTML индекс для просмотра всех PNG."""
        print("📄 Создание индекса HTML...\n")

        png_files = sorted(self.output_dir.glob("*.png"))

        if not png_files:
            print("⚠️  PNG файлы не найдены")
            return False

        html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Диаграммы системы</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(700px, 1fr));
            gap: 20px;
        }
        
        .diagram {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .diagram h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .diagram img {
            width: 100%;
            height: auto;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Диаграммы системы</h1>
            <p>Система детектирования мошенничества в реальном времени</p>
        </header>
        
        <div class="grid">
"""

        diagram_names = {
            "01_dataflow": "Поток данных (Data Flow)",
            "02_architecture": "Архитектура системы",
            "03_ensemble_voting": "Ансамблевое голосование",
            "04_components": "Компоненты системы",
            "05_decision_tree": "Дерево решений",
            "06_model_ensemble": "Обучение моделей",
            "07_security_logging": "Логирование и аудит",
        }

        for png_file in png_files:
            stem = png_file.stem
            name = diagram_names.get(stem, stem)

            html_content += f"""        <div class="diagram">
            <h3>{name}</h3>
            <img src="images/{png_file.name}" alt="{name}">
        </div>
"""

        html_content += """        </div>
        
        <footer>
            <p>📊 Версия 3.0 | Дата создания: 15.05.2026</p>
        </footer>
    </div>
</body>
</html>"""

        html_file = self.diagrams_dir.parent / "diagrams_images.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✓ Создан: {html_file}")
        return True

    def run(self):
        """Запускает полный процесс."""
        print("=" * 70)
        print("🎨 ЭКСПОРТ ДИАГРАММ В PNG")
        print("=" * 70 + "\n")

        # Проверка зависимостей
        if not self.check_dependencies():
            print("\n⚠️  Требуются зависимости. Установите Node.js и npm.")
            return False

        # Установка Mermaid CLI
        if not self.install_mermaid_cli():
            print("\n❌ Не удалось установить Mermaid CLI")
            print("\nПопробуйте вручную:")
            print("  npm install -g @mermaid-js/mermaid-cli")
            return False

        # Экспорт диаграмм
        if not self.export_diagrams():
            print("\n❌ Ошибка при экспорте диаграмм")
            return False

        # Создание HTML индекса
        if self.create_index_html():
            print("\n✅ Все диаграммы успешно экспортированы!")
            print(f"\n📂 PNG файлы в: {self.output_dir}")
            print(f"📄 Просмотр: docs/diagrams_images.html")
            print("\n💡 Откройте в браузере: open docs/diagrams_images.html")
            return True

        return False


def main():
    """Главная функция."""
    try:
        exporter = DiagramExporter()
        success = exporter.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
