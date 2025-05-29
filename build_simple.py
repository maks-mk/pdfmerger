#!/usr/bin/env python3
"""
Упрощенный скрипт сборки PDF Merger Pro v2.1
Для быстрой сборки без дополнительных проверок
"""

import PyInstaller.__main__
from pathlib import Path

def main():
    """Простая сборка приложения."""
    print("🚀 Быстрая сборка PDF Merger Pro v2.1")
    
    script_dir = Path(__file__).parent
    main_script = script_dir / 'main.py'
    icon_file = script_dir / 'pdf.ico'
    
    # Проверяем основной файл
    if not main_script.exists():
        print(f"❌ Файл main.py не найден: {main_script}")
        return
    
    # Параметры для PyInstaller
    args = [
        '--onefile',
        '--windowed',
        '--name=PDFMergerPro',
        '--clean',
        '--noconfirm',
    ]
    
    # Добавляем иконку если есть
    if icon_file.exists():
        args.append(f'--icon={icon_file}')
    
    # Добавляем скрытые импорты
    hidden_imports = [
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PyPDF2',
        'qtawesome',
        'qtawesome.iconic_font',
    ]
    
    for imp in hidden_imports:
        args.extend(['--hidden-import', imp])
    
    # Добавляем основной скрипт
    args.append(str(main_script))
    
    print("🔨 Запуск PyInstaller...")
    try:
        PyInstaller.__main__.run(args)
        print("✅ Сборка завершена!")
        
        # Проверяем результат
        exe_file = script_dir / 'dist' / 'PDFMergerPro.exe'
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)
            print(f"📦 Файл: {exe_file}")
            print(f"📏 Размер: {file_size:.1f} МБ")
        
    except Exception as e:
        print(f"❌ Ошибка сборки: {e}")

if __name__ == '__main__':
    main()
