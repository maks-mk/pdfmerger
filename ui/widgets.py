"""
Пользовательские виджеты для PDF Merger Pro
"""

import os
from PyQt6.QtWidgets import QListWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class PDFListWidget(QListWidget):
    """Список PDF файлов с поддержкой drag & drop."""

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # Улучшенный placeholder для пустого списка
        self.setStyleSheet("""
            QListWidget {
                border: 2px dashed #adb5bd;
                border-radius: 12px;
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 14px;
                text-align: center;
                padding: 40px;
            }
            QListWidget:focus {
                border-color: #667eea;
                background-color: #f8f9fa;
            }
        """)

        # Добавляем placeholder текст
        self.placeholder_text = "📁 Перетащите файлы сюда\n(PDF, Word, изображения, текст)\nили используйте кнопку 'Добавить файлы'"
        self.update_placeholder()

    def update_placeholder(self):
        """Обновляет отображение placeholder текста"""
        if self.count() == 0:
            # Показываем placeholder
            self.setStyleSheet("""
                QListWidget {
                    border: 2px dashed #adb5bd;
                    border-radius: 12px;
                    background-color: #f8f9fa;
                    color: #6c757d;
                    font-size: 14px;
                    text-align: center;
                    padding: 40px;
                }
                QListWidget:focus {
                    border-color: #667eea;
                    background-color: #f8f9fa;
                }
            """)
        else:
            # Обычный стиль для списка с элементами
            self.setStyleSheet("")

    def addItem(self, item):
        """Переопределяем для обновления placeholder"""
        super().addItem(item)
        self.update_placeholder()

    def clear(self):
        """Переопределяем для обновления placeholder"""
        super().clear()
        self.update_placeholder()

    def takeItem(self, row):
        """Переопределяем для обновления placeholder"""
        result = super().takeItem(row)
        self.update_placeholder()
        return result

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обработка входа при перетаскивании"""
        mime_data = event.mimeData()
        if mime_data and mime_data.hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Обработка сброса файлов"""
        mime_data = event.mimeData()
        if mime_data and mime_data.hasUrls():
            files = []
            # Поддерживаемые расширения
            supported_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.bmp']

            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    # Проверяем расширение файла
                    if any(file_path.lower().endswith(ext) for ext in supported_extensions):
                        files.append(file_path)

            if files:
                # Добавляем только уникальные файлы
                existing_files = []
                for i in range(self.count()):
                    item = self.item(i)
                    if item:
                        existing_files.append(item.text())
                for file_path in files:
                    if file_path and file_path not in existing_files:
                        self.addItem(file_path)
                event.accept()
            else:
                event.ignore()
        else:
            super().dropEvent(event)


class StatusWidget(QLabel):
    """Виджет для отображения статуса с иконкой."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('status')
        self.setText('Готов к работе')

    def set_status(self, text, status_type='info'):
        """Устанавливает статус с соответствующим стилем."""
        self.setText(text)

        color_map = {
            'info': '#17a2b8',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'processing': '#6f42c1'
        }

        color = color_map.get(status_type, '#17a2b8')
        self.setStyleSheet(f"""
            QLabel#status {{
                color: {color};
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 500;
                padding: 8px 12px;
                background-color: white;
                border-radius: 6px;
                border: 1px solid #e9ecef;
            }}
        """)


class FileCountWidget(QLabel):
    """Виджет для отображения количества файлов."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            font-weight: 500;
            background-color: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
        """)
        self.update_count(0)

    def update_count(self, count):
        """Обновляет отображение количества файлов."""
        self.setText(f'Файлов: {count}')

        # Меняем цвет в зависимости от количества
        if count == 0:
            bg_color = '#e9ecef'
            text_color = '#6c757d'
        elif count == 1:
            bg_color = '#fff3cd'
            text_color = '#856404'
        else:
            bg_color = '#d4edda'
            text_color = '#155724'

        self.setStyleSheet(f"""
            color: {text_color};
            font-size: 12px;
            font-weight: 500;
            background-color: {bg_color};
            padding: 4px 8px;
            border-radius: 4px;
        """)


class CompactButton:
    """Фабрика для создания компактных кнопок."""

    @staticmethod
    def create_button(text, icon_name=None, color='#495057', style_type='normal'):
        """Создает кнопку с заданными параметрами."""
        from PyQt6.QtWidgets import QPushButton
        import qtawesome as qta

        button = QPushButton(text)

        if icon_name:
            button.setIcon(qta.icon(icon_name, color=color))

        style_map = {
            'success': {'border': '#28a745', 'hover': '#28a745'},
            'info': {'border': '#17a2b8', 'hover': '#17a2b8'},
            'warning': {'border': '#ffc107', 'hover': '#ffc107'},
            'danger': {'border': '#dc3545', 'hover': '#dc3545'},
            'normal': {'border': '#e9ecef', 'hover': '#6c757d'}
        }

        style = style_map.get(style_type, style_map['normal'])

        button.setStyleSheet(f"""
            QPushButton {{
                border-color: {style['border']};
                color: {color};
            }}
            QPushButton:hover {{
                background-color: {style['hover']};
                color: white;
            }}
        """)

        return button
