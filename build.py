#!/usr/bin/env python3
"""
Скрипт сборки PDF Merger Pro v2.1
Создает исполняемый файл из модульной структуры приложения
"""

import PyInstaller.__main__
import sys
from pathlib import Path

def check_dependencies():
    """Проверяет наличие необходимых зависимостей для сборки."""
    missing_deps = []

    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        missing_deps.append("PyInstaller")

    try:
        from PyQt6.QtCore import qVersion
        print(f"✅ PyQt6 {qVersion()}")
    except ImportError:
        missing_deps.append("PyQt6")

    try:
        import PyPDF2
        print(f"✅ PyPDF2 {PyPDF2.__version__}")
    except ImportError:
        missing_deps.append("PyPDF2")

    try:
        import qtawesome
        print(f"✅ qtawesome {qtawesome.__version__}")
    except ImportError:
        missing_deps.append("qtawesome")

    try:
        import fitz
        print(f"✅ PyMuPDF {fitz.version[0]}")
    except ImportError:
        print("⚠️  PyMuPDF не установлен (предпросмотр будет недоступен)")

    if missing_deps:
        print(f"\n❌ Отсутствуют зависимости: {', '.join(missing_deps)}")
        print("Установите их: pip install " + " ".join(missing_deps))
        return False

    return True

def get_build_info():
    """Получает информацию о сборке."""
    script_dir = Path(__file__).parent

    # Основной скрипт (новая модульная версия)
    main_script = script_dir / 'main.py'

    # Файл иконки
    icon_file = script_dir / 'pdf.ico'

    # Проверяем существование файлов
    if not main_script.exists():
        print(f"❌ Основной скрипт не найден: {main_script}")
        return None

    if not icon_file.exists():
        print(f"⚠️  Файл иконки не найден: {icon_file}")
        icon_file = None

    return {
        'main_script': str(main_script),
        'icon_file': str(icon_file) if icon_file else None,
        'script_dir': str(script_dir)
    }

def create_spec_content(build_info):
    """Создает содержимое .spec файла для более точной сборки."""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{build_info["main_script"]}'],
    pathex=['{build_info["script_dir"]}'],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('core', 'core'),
        ('README.md', '.'),
        ('USAGE.md', '.'),
        ('MULTIPREVIEW.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyPDF2',
        'qtawesome',
        'qtawesome.iconic_font',
        'fitz',  # PyMuPDF
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFMergerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,'''

    if build_info['icon_file']:
        spec_content += f"\n    icon='{build_info['icon_file']}',"

    spec_content += "\n)\n"

    return spec_content

def build_application():
    """Основная функция сборки приложения."""
    print("🚀 Начинаем сборку PDF Merger Pro v2.1")
    print("=" * 50)

    # Проверяем зависимости
    print("📦 Проверка зависимостей...")
    if not check_dependencies():
        return False

    print("\n📁 Получение информации о сборке...")
    build_info = get_build_info()
    if not build_info:
        return False

    print(f"✅ Основной скрипт: {build_info['main_script']}")
    if build_info['icon_file']:
        print(f"✅ Иконка: {build_info['icon_file']}")

    # Создаем .spec файл для более точной сборки
    print("\n📝 Создание .spec файла...")
    spec_file = Path(build_info['script_dir']) / 'PDFMergerPro.spec'
    spec_content = create_spec_content(build_info)

    try:
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        print(f"✅ Создан .spec файл: {spec_file}")
    except Exception as e:
        print(f"❌ Ошибка создания .spec файла: {e}")
        return False

    # Параметры для PyInstaller
    print("\n🔨 Запуск PyInstaller...")
    pyinstaller_args = [
        str(spec_file),
        '--clean',  # Очистить кэш
        '--noconfirm',  # Не спрашивать подтверждения
    ]

    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n✅ Сборка завершена успешно!")

        # Информация о результате
        dist_dir = Path(build_info['script_dir']) / 'dist'
        exe_file = dist_dir / 'PDFMergerPro.exe'

        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 Исполняемый файл: {exe_file}")
            print(f"📏 Размер файла: {file_size:.1f} МБ")
            print(f"📂 Папка сборки: {dist_dir}")

        return True

    except Exception as e:
        print(f"\n❌ Ошибка сборки: {e}")
        return False

    finally:
        # Очищаем временные файлы
        try:
            if spec_file.exists():
                spec_file.unlink()
                print(f"🧹 Удален временный .spec файл")
        except Exception:
            pass

def main():
    """Главная функция."""
    try:
        success = build_application()

        if success:
            print("\n🎉 Сборка PDF Merger Pro завершена!")
            print("📋 Что дальше:")
            print("   1. Найдите исполняемый файл в папке 'dist'")
            print("   2. Протестируйте приложение")
            print("   3. Распространяйте готовый файл")
            sys.exit(0)
        else:
            print("\n💥 Сборка завершилась с ошибками")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Сборка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
