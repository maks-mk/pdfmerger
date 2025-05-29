#!/usr/bin/env python3
"""
PDF Merger Pro - Приложение для объединения PDF файлов
Версия: 2.2
Автор: PDF Merger Team

Главный файл запуска приложения
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Основные импорты PyQt6
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Проверка зависимостей
def check_dependencies():
    """Проверяет наличие всех необходимых зависимостей."""
    missing_deps = []

    # Проверяем PyPDF2
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append("PyPDF2")

    # Проверяем qtawesome
    try:
        import qtawesome
    except ImportError:
        missing_deps.append("qtawesome")

    # Проверяем PyMuPDF (опционально)
    try:
        import fitz
    except ImportError:
        print("⚠️  PyMuPDF не установлен. Предварительный просмотр будет недоступен.")
        print("   Установите PyMuPDF: pip install PyMuPDF")

    if missing_deps:
        error_msg = "Отсутствуют необходимые зависимости:\n\n"
        for dep in missing_deps:
            error_msg += f"• {dep}\n"
        error_msg += "\nУстановите зависимости:\n"
        error_msg += f"pip install {' '.join(missing_deps)}"

        print(f"❌ {error_msg}")
        return False, error_msg

    return True, "Все зависимости установлены"


def setup_application():
    """Настройка приложения."""
    app = QApplication(sys.argv)

    # Настройки приложения
    app.setApplicationName("PDF Merger Pro")
    app.setApplicationVersion("2.2")
    app.setOrganizationName("PDF Merger Team")

    # Установка иконки приложения
    try:
        import qtawesome as qta
        app.setWindowIcon(qta.icon('fa5s.file-pdf', color='#667eea'))
    except Exception:
        pass

    # Настройка высокого DPI для PyQt6
    try:
        # В PyQt6 автоматическое масштабирование включено по умолчанию
        # Используем только безопасные атрибуты
        app.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, False)
    except AttributeError:
        # Игнорируем ошибки атрибутов для совместимости
        pass

    return app


def main():
    """Главная функция приложения."""
    print("🚀 Запуск PDF Merger Pro v2.2")

    # Проверяем зависимости
    deps_ok, deps_message = check_dependencies()
    if not deps_ok:
        # Показываем ошибку через консоль и GUI (если возможно)
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Ошибка зависимостей",
                deps_message
            )
        except Exception:
            pass
        sys.exit(1)

    print("✅ Все зависимости проверены")

    # Создаем приложение
    app = setup_application()

    try:
        # Импортируем главное окно
        from ui.main_window import PDFMergerMainWindow

        print("🎨 Создание главного окна...")

        # Создаем и показываем главное окно
        window = PDFMergerMainWindow()
        window.show()

        print("✨ Приложение готово к работе!")
        print("📁 Перетащите PDF файлы в окно или используйте кнопку 'Добавить файлы'")

        # Запускаем главный цикл приложения
        sys.exit(app.exec())

    except ImportError as e:
        error_msg = f"Ошибка импорта модулей: {str(e)}"
        print(f"❌ {error_msg}")

        try:
            QMessageBox.critical(
                None,
                "Ошибка импорта",
                error_msg
            )
        except Exception:
            pass
        sys.exit(1)

    except Exception as e:
        error_msg = f"Неожиданная ошибка: {str(e)}"
        print(f"💥 {error_msg}")

        try:
            QMessageBox.critical(
                None,
                "Критическая ошибка",
                error_msg
            )
        except Exception:
            pass
        sys.exit(1)


if __name__ == '__main__':
    main()
