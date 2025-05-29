"""
Стили для PDF Merger Pro
"""

APP_STYLES = """
QMainWindow {
    background-color: #f8f9fa;
    color: #212529;
}

/* Карточка для списка файлов */
QListWidget {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    padding: 16px;
    font-size: 14px;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Стили для полосы прокрутки */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #adb5bd;
    border-radius: 6px;
    min-height: 20px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background-color: #6c757d;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QListWidget::item {
    padding: 12px 16px;
    border: none;
    border-radius: 8px;
    margin: 2px 0;
    background-color: transparent;
    color: #495057;
}
QListWidget::item:hover {
    background-color: #f8f9fa;
    color: #212529;
}
QListWidget::item:selected {
    background-color: #667eea;
    color: white;
    font-weight: 500;
}

/* Современные кнопки */
QPushButton {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #495057;
    min-width: 100px;
    max-height: 36px;
}
QPushButton:hover {
    background-color: #f8f9fa;
    border-color: #6c757d;
    color: #212529;
}
QPushButton:pressed {
    background-color: #e9ecef;
}
QPushButton:disabled {
    background-color: #f8f9fa;
    color: #adb5bd;
    border-color: #e9ecef;
}

/* Главная кнопка объединения */
QPushButton#merge_btn {
    background-color: #667eea;
    color: white;
    border: none;
    font-weight: 600;
    font-size: 14px;
    padding: 12px 20px;
    max-height: 44px;
}
QPushButton#merge_btn:hover {
    background-color: #5a6fd8;
}
QPushButton#merge_btn:pressed {
    background-color: #4e63d2;
}
QPushButton#merge_btn:disabled {
    background-color: #adb5bd;
    color: #6c757d;
}

/* Кнопка предпросмотра */
QPushButton#preview_all_btn {
    background-color: #11998e;
    color: white;
    border: none;
    font-weight: 600;
    padding: 10px 16px;
    max-height: 40px;
}
QPushButton#preview_all_btn:hover {
    background-color: #0f8a7e;
}

/* Заголовки и текст */
QLabel#title {
    color: #212529;
    font-size: 18px;
    font-weight: 700;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QLabel#subtitle {
    color: #6c757d;
    font-size: 14px;
    font-family: 'Segoe UI', Arial, sans-serif;
    margin-bottom: 8px;
}
QLabel#status {
    color: #495057;
    font-size: 13px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-weight: 500;
    padding: 8px 12px;
    background-color: white;
    border-radius: 6px;
    border: 1px solid #e9ecef;
}

/* Группы кнопок */
QWidget#button_group {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 12px;
    margin: 4px 0;
}
"""

DIALOG_STYLES = """
QDialog {
    background-color: #f8f9fa;
    color: #212529;
}
QLabel#page_display {
    font-size: 14px;
    color: #495057;
    padding: 8px 12px;
    background-color: white;
    border-radius: 6px;
    font-weight: 500;
}
QComboBox {
    border: 2px solid #e9ecef;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 120px;
    font-size: 13px;
    background-color: white;
}
QComboBox:hover {
    border-color: #6c757d;
}
QComboBox:focus {
    border-color: #667eea;
}
QPushButton, QToolButton {
    background-color: white;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #495057;
    min-width: 80px;
}
QPushButton:hover, QToolButton:hover {
    background-color: #f8f9fa;
    border-color: #6c757d;
}
QPushButton:pressed, QToolButton:pressed {
    background-color: #e9ecef;
}
QScrollArea {
    border: none;
    background-color: white;
    border-radius: 12px;
}
QLabel {
    color: #495057;
    font-family: 'Segoe UI', Arial, sans-serif;
}
"""
