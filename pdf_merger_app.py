import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QListWidget, QPushButton, QFileDialog,
                             QMessageBox, QLabel, QDialog, QScrollArea,
                             QComboBox, QSplitter, QToolButton)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPixmap, QImage
import qtawesome as qta

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("Установите PyPDF2: pip install PyPDF2")
    sys.exit(1)

try:
    import fitz # Импортируем PyMuPDF
except ImportError:
    print("Установите PyMuPDF для предварительного просмотра: pip install PyMuPDF")
    # Приложение может работать без предварительного просмотра, но с предупреждением
    fitz = None

# Добавляем игнорирование проверки типов для PyMuPDF
# pyright: reportAttributeAccessIssue=false

class PDFMergerWorker(QThread):
    """Рабочий поток для объединения PDF файлов."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    # Optional: progress = pyqtSignal(int) # Для индикатора прогресса по страницам/файлам

    def __init__(self, file_paths, output_path):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path

    def run(self):
        merger = PdfWriter()
        try:
            for file_path in self.file_paths:
                if not os.path.exists(file_path):
                    self.error.emit(f"Файл не найден: {os.path.basename(file_path)}")
                    return

                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PdfReader(pdf_file)
                    # Optional: self.progress.emit(...) # Emit progress for each file or page
                    for page in pdf_reader.pages:
                         merger.add_page(page)

            with open(self.output_path, 'wb') as output:
                merger.write(output)

            self.finished.emit(self.output_path)

        except Exception as e:
            self.error.emit(f"Ошибка при объединении файлов: {str(e)}")


class PDFListWidget(QListWidget):
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
        self.placeholder_text = "📁 Перетащите PDF файлы сюда\nили используйте кнопку 'Добавить файлы'"
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
        mime_data = event.mimeData()
        if mime_data and mime_data.hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data and mime_data.hasUrls():
            files = []
            for url in mime_data.urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.pdf'):
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


class PDFMultiPreviewDialog(QDialog):
    """Диалог для предварительного просмотра всех PDF-файлов перед объединением"""

    def __init__(self, parent=None, file_paths=None):
        super().__init__(parent)
        self.file_paths = file_paths or []
        self.current_file_index = 0
        self.current_page = 0
        self.doc = None
        self.zoom_factor = 1.0

        self.init_ui()
        self.load_current_file()

    def init_ui(self):
        self.setWindowTitle('Предпросмотр всех файлов')
        # Адаптируем под низкие разрешения
        self.setGeometry(50, 20, 900, 650)
        self.setMinimumSize(800, 550)
        self.setMaximumSize(1100, 750)

        # Современный дизайн для мультипредпросмотра
        self.setStyleSheet("""
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
            QPushButton, QToolButton {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
                color: #495057;
                min-width: 100px;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #f8f9fa;
                border-color: #6c757d;
            }
            QScrollArea {
                border: none;
                background-color: white;
                border-radius: 12px;
            }
            QListWidget {
                border: none;
                border-radius: 8px;
                background-color: white;
                padding: 12px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border: none;
                border-radius: 6px;
                margin: 2px 0;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: 500;
            }
            QLabel {
                color: #495057;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        # Компактный макет с разделителем
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 10, 12, 10)

        # Компактный заголовок
        title_label = QLabel('Предпросмотр файлов')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #333; margin-bottom: 6px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Создаем разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - список файлов
        file_panel = QWidget()
        file_layout = QVBoxLayout(file_panel)
        file_layout.setContentsMargins(0, 0, 10, 0)

        file_list_label = QLabel('Список файлов:')
        file_list_label.setStyleSheet("font-weight: bold;")
        file_layout.addWidget(file_list_label)

        self.file_list_widget = QListWidget()
        self.file_list_widget.setMinimumWidth(200)
        self.file_list_widget.currentRowChanged.connect(self.change_file)

        # Заполняем список файлов
        for file_path in self.file_paths:
            self.file_list_widget.addItem(os.path.basename(file_path))

        file_layout.addWidget(self.file_list_widget, 1)
        splitter.addWidget(file_panel)

        # Правая панель - просмотр PDF
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(10, 0, 0, 0)

        # Компактная панель управления в две строки
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(4)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Первая строка - информация о файле
        info_panel = QHBoxLayout()
        info_panel.setSpacing(8)

        # Информация о файле
        self.file_info_label = QLabel()
        self.file_info_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_panel.addWidget(self.file_info_label)
        info_panel.addStretch()
        controls_layout.addLayout(info_panel)

        # Вторая строка - навигация и масштаб
        nav_panel = QHBoxLayout()
        nav_panel.setSpacing(8)

        # Кнопки навигации по страницам
        self.prev_btn = QToolButton()
        self.prev_btn.setIcon(qta.icon('fa5s.chevron-left'))
        self.prev_btn.setToolTip('Предыдущая страница')
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setFixedSize(28, 28)
        nav_panel.addWidget(self.prev_btn)

        # Отображение текущей/всего страниц
        self.page_label = QLabel('Страница: 0 / 0')
        self.page_label.setObjectName('page_display')
        self.page_label.setMinimumWidth(100)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_panel.addWidget(self.page_label)

        self.next_btn = QToolButton()
        self.next_btn.setIcon(qta.icon('fa5s.chevron-right'))
        self.next_btn.setToolTip('Следующая страница')
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setFixedSize(28, 28)
        nav_panel.addWidget(self.next_btn)

        nav_panel.addStretch()

        # Выбор масштаба
        zoom_label = QLabel('Масштаб:')
        zoom_label.setStyleSheet("font-size: 11px;")
        nav_panel.addWidget(zoom_label)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(['50%', '75%', '100%', '125%', '150%', '200%'])
        self.zoom_combo.setCurrentText('100%')
        self.zoom_combo.currentTextChanged.connect(self.change_zoom)
        self.zoom_combo.setMinimumWidth(70)
        nav_panel.addWidget(self.zoom_combo)

        controls_layout.addLayout(nav_panel)
        preview_layout.addWidget(controls_widget)

        # Область просмотра
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Важно: False для правильной прокрутки больших страниц
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Метка для отображения изображения (без контейнера)
        self.preview_label = QLabel('Выберите PDF файл для просмотра')
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white;")

        # Устанавливаем метку как виджет для прокрутки
        self.scroll_area.setWidget(self.preview_label)

        preview_layout.addWidget(self.scroll_area, 1)

        splitter.addWidget(preview_panel)

        # Устанавливаем соотношение разделителя
        splitter.setSizes([200, 700])  # Примерное соотношение сторон

        main_layout.addWidget(splitter, 1)

        # Нижняя панель с кнопками навигации по файлам
        bottom_panel = QHBoxLayout()

        self.prev_file_btn = QPushButton('Предыдущий файл')
        self.prev_file_btn.setIcon(qta.icon('fa5s.file-pdf'))
        self.prev_file_btn.clicked.connect(self.prev_file)
        bottom_panel.addWidget(self.prev_file_btn)

        bottom_panel.addStretch()

        self.next_file_btn = QPushButton('Следующий файл')
        self.next_file_btn.setIcon(qta.icon('fa5s.file-pdf'))
        self.next_file_btn.clicked.connect(self.next_file)
        bottom_panel.addWidget(self.next_file_btn)

        main_layout.addLayout(bottom_panel)

        # Кнопки OK/Отмена
        buttons_panel = QHBoxLayout()
        buttons_panel.addStretch()

        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.close)
        buttons_panel.addWidget(close_btn)

        main_layout.addLayout(buttons_panel)

        # Начальное состояние кнопок
        self.update_navigation()

    def load_current_file(self):
        """Загрузить текущий PDF файл для просмотра"""
        # Закрываем предыдущий документ, если он открыт
        if self.doc:
            self.doc.close()  # type: ignore
            self.doc = None

        if not self.file_paths or self.current_file_index >= len(self.file_paths):
            self.preview_label.setText("Нет файлов для предварительного просмотра")
            self.update_navigation()
            return

        if not fitz:
            self.preview_label.setText("PyMuPDF не установлен.\nУстановите библиотеку: pip install PyMuPDF")
            self.update_navigation()
            return

        try:
            file_path = self.file_paths[self.current_file_index]
            if not os.path.exists(file_path):
                self.preview_label.setText(f"Файл не найден: {os.path.basename(file_path)}")
                self.update_navigation()
                return

            self.doc = fitz.open(file_path)  # type: ignore
            self.current_page = 0

            # Обновляем информацию о файле и страницах
            self.file_info_label.setText(f'Файл: {os.path.basename(file_path)}')
            self.page_label.setText(f'Страница: 1 / {len(self.doc)}')

            # Выделяем текущий файл в списке
            self.file_list_widget.setCurrentRow(self.current_file_index)

            # Отображаем первую страницу
            self.display_page()

            # Обновляем состояние кнопок навигации
            self.update_navigation()
        except Exception as e:
            self.preview_label.setText(f"Ошибка при загрузке PDF: {str(e)}")
            self.update_navigation()

    def display_page(self):
        """Отобразить текущую страницу PDF"""
        if not self.doc or self.current_page < 0 or self.current_page >= len(self.doc):
            return

        try:
            # Получаем страницу
            page = self.doc[self.current_page]

            # Устанавливаем масштаб
            zoom = self.zoom_factor

            # Рендерим страницу
            if fitz:  # Проверяем, что fitz импортирован успешно
                # type: ignore - игнорирование проверки типов для PyMuPDF
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))  # type: ignore
            else:
                return

            # Преобразуем в QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

            # Преобразуем в QPixmap и отображаем
            pixmap = QPixmap.fromImage(img)
            self.preview_label.setPixmap(pixmap)

            # Изменяем размер метки в соответствии с размером изображения
            self.preview_label.resize(pixmap.size())

            # Обновляем информацию о текущей странице
            self.page_label.setText(f'Страница: {self.current_page + 1} / {len(self.doc)}')

            # Обновляем состояние кнопок навигации
            self.update_navigation()
        except Exception as e:
            self.preview_label.setText(f"Ошибка при отображении страницы: {str(e)}")
            self.update_navigation()

    def prev_page(self):
        """Перейти к предыдущей странице"""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def next_page(self):
        """Перейти к следующей странице"""
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.display_page()

    def prev_file(self):
        """Перейти к предыдущему файлу"""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.load_current_file()

    def next_file(self):
        """Перейти к следующему файлу"""
        if self.current_file_index < len(self.file_paths) - 1:
            self.current_file_index += 1
            self.load_current_file()

    def change_file(self, row):
        """Изменить текущий файл по выбору в списке"""
        if 0 <= row < len(self.file_paths):
            self.current_file_index = row
            self.load_current_file()

    def change_zoom(self, zoom_text):
        """Изменить масштаб отображения"""
        try:
            zoom_value = float(zoom_text.rstrip('%')) / 100.0
            self.zoom_factor = zoom_value

            if self.doc:
                self.display_page()
        except ValueError:
            pass

    def update_navigation(self):
        """Обновить состояние кнопок навигации"""
        has_files = len(self.file_paths) > 0
        has_doc = self.doc is not None

        # Получаем количество страниц безопасно
        doc_page_count = 0
        if has_doc and self.doc is not None:
            try:
                doc_page_count = len(self.doc)
            except (AttributeError, TypeError):
                doc_page_count = 0

        doc_has_pages = doc_page_count > 0

        # Навигация по страницам
        self.prev_btn.setEnabled(has_doc and self.current_page > 0)
        self.next_btn.setEnabled(doc_has_pages and self.current_page < doc_page_count - 1)

        # Навигация по файлам
        self.prev_file_btn.setEnabled(has_files and self.current_file_index > 0)
        self.next_file_btn.setEnabled(has_files and self.current_file_index < len(self.file_paths) - 1)

        # Масштабирование
        self.zoom_combo.setEnabled(doc_has_pages)

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.doc:
            self.doc.close()  # type: ignore
        event.accept()


class PDFMergerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None # Для хранения ссылки на рабочий поток
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('PDF Merger Pro')
        # Адаптируем под низкие разрешения (1366x768)
        self.setGeometry(50, 30, 650, 600)
        self.setMinimumSize(600, 500)
        self.setMaximumSize(800, 700)

        # Современная цветовая схема (без неподдерживаемых свойств)
        self.setStyleSheet("""
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
        """)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Компактный layout для низких разрешений
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 12, 16, 12)

        # Современный заголовок
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Компактная иконка
        icon_label = QLabel()
        icon_size = 32
        qt_icon = qta.icon('fa5s.file-pdf', color='#667eea')
        icon_pixmap = qt_icon.pixmap(icon_size, icon_size)
        icon_label.setPixmap(icon_pixmap)
        header_layout.addWidget(icon_label)

        # Заголовок с улучшенной типографикой
        title_label = QLabel('PDF Merger Pro')
        title_label.setObjectName('title')
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Добавляем информацию о версии
        version_label = QLabel('v2.0')
        version_label.setStyleSheet("""
            color: #adb5bd;
            font-size: 12px;
            font-weight: 500;
            background-color: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
        """)
        header_layout.addWidget(version_label)

        main_layout.addLayout(header_layout)

        # Улучшенный подзаголовок
        subtitle_label = QLabel('Перетащите PDF файлы в область ниже или используйте кнопки для добавления')
        subtitle_label.setObjectName('subtitle')
        main_layout.addWidget(subtitle_label)

        # Компактный список файлов с прокруткой
        self.file_list = PDFListWidget()
        self.file_list.setMinimumHeight(180)
        self.file_list.setMaximumHeight(250)
        # Явно включаем вертикальную прокрутку
        self.file_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(self.file_list)

        # Группа кнопок управления файлами
        file_controls_group = QWidget()
        file_controls_group.setObjectName('button_group')
        file_controls_layout = QVBoxLayout(file_controls_group)
        file_controls_layout.setContentsMargins(0, 0, 0, 0)
        file_controls_layout.setSpacing(6)

        # Заголовок группы
        controls_title = QLabel('Управление файлами')
        controls_title.setStyleSheet("""
            color: #495057;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        """)
        file_controls_layout.addWidget(controls_title)

        # Основные кнопки управления
        main_controls_layout = QHBoxLayout()
        main_controls_layout.setSpacing(8)

        # Кнопка добавления с улучшенным дизайном
        self.add_btn = QPushButton('Добавить файлы')
        self.add_btn.setIcon(qta.icon('fa5s.plus', color='#28a745'))
        self.add_btn.clicked.connect(self.add_files)
        self.add_btn.setStyleSheet("""
            QPushButton {
                border-color: #28a745;
                color: #28a745;
            }
            QPushButton:hover {
                background-color: #28a745;
                color: white;
            }
        """)
        main_controls_layout.addWidget(self.add_btn)

        # Кнопка предварительного просмотра
        self.preview_btn = QPushButton('Просмотр')
        self.preview_btn.setIcon(qta.icon('fa5s.eye', color='#17a2b8'))
        self.preview_btn.clicked.connect(self.preview_pdf)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                border-color: #17a2b8;
                color: #17a2b8;
            }
            QPushButton:hover {
                background-color: #17a2b8;
                color: white;
            }
        """)
        main_controls_layout.addWidget(self.preview_btn)

        main_controls_layout.addStretch()

        # Кнопки перемещения
        move_controls_layout = QHBoxLayout()
        move_controls_layout.setSpacing(8)

        self.move_up_btn = QPushButton()
        self.move_up_btn.setIcon(qta.icon('fa5s.arrow-up', color='#6c757d'))
        self.move_up_btn.setToolTip('Переместить вверх')
        self.move_up_btn.clicked.connect(self.move_up)
        self.move_up_btn.setFixedSize(40, 40)
        move_controls_layout.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton()
        self.move_down_btn.setIcon(qta.icon('fa5s.arrow-down', color='#6c757d'))
        self.move_down_btn.setToolTip('Переместить вниз')
        self.move_down_btn.clicked.connect(self.move_down)
        self.move_down_btn.setFixedSize(40, 40)
        move_controls_layout.addWidget(self.move_down_btn)

        main_controls_layout.addLayout(move_controls_layout)
        file_controls_layout.addLayout(main_controls_layout)

        # Дополнительные кнопки
        secondary_controls_layout = QHBoxLayout()
        secondary_controls_layout.setSpacing(8)

        # Кнопка удаления
        self.remove_btn = QPushButton('Удалить выбранный')
        self.remove_btn.setIcon(qta.icon('fa5s.trash', color='#dc3545'))
        self.remove_btn.clicked.connect(self.remove_file)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                border-color: #dc3545;
                color: #dc3545;
            }
            QPushButton:hover {
                background-color: #dc3545;
                color: white;
            }
        """)
        secondary_controls_layout.addWidget(self.remove_btn)

        # Кнопка очистки
        self.clear_btn = QPushButton('Очистить все')
        self.clear_btn.setIcon(qta.icon('fa5s.broom', color='#ffc107'))
        self.clear_btn.clicked.connect(self.clear_list)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                border-color: #ffc107;
                color: #856404;
            }
            QPushButton:hover {
                background-color: #ffc107;
                color: #212529;
            }
        """)
        secondary_controls_layout.addWidget(self.clear_btn)

        secondary_controls_layout.addStretch()
        file_controls_layout.addLayout(secondary_controls_layout)

        main_layout.addWidget(file_controls_group)

        # Группа основных действий
        action_group = QWidget()
        action_group.setObjectName('button_group')
        action_layout = QVBoxLayout(action_group)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(6)

        # Заголовок группы действий
        action_title = QLabel('Действия')
        action_title.setStyleSheet("""
            color: #495057;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        """)
        action_layout.addWidget(action_title)

        # Кнопка предпросмотра всех файлов
        self.preview_all_btn = QPushButton('🔍 Предпросмотр всех файлов')
        self.preview_all_btn.setObjectName('preview_all_btn')
        self.preview_all_btn.setIcon(qta.icon('fa5s.eye', color='white'))
        self.preview_all_btn.clicked.connect(self.preview_all_pdfs)
        action_layout.addWidget(self.preview_all_btn)

        # Главная кнопка объединения
        self.merge_btn = QPushButton('🚀 Объединить PDF файлы')
        self.merge_btn.setObjectName('merge_btn')
        self.merge_btn.setIcon(qta.icon('fa5s.magic', color='white'))
        self.merge_btn.clicked.connect(self.merge_pdfs)
        action_layout.addWidget(self.merge_btn)

        main_layout.addWidget(action_group)

        # Улучшенная панель статуса
        status_group = QWidget()
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(12)

        # Иконка статуса
        self.status_icon = QLabel()
        status_icon_pixmap = qta.icon('fa5s.check-circle', color='#28a745').pixmap(16, 16)
        self.status_icon.setPixmap(status_icon_pixmap)
        status_layout.addWidget(self.status_icon)

        # Текст статуса
        self.status_label = QLabel('Готов к работе')
        self.status_label.setObjectName('status')
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        # Счетчик файлов
        self.file_count_label = QLabel('Файлов: 0')
        self.file_count_label.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            font-weight: 500;
            background-color: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
        """)
        status_layout.addWidget(self.file_count_label)

        main_layout.addWidget(status_group)

        # Обновление счетчика при изменении списка
        self.file_list.itemChanged.connect(self.update_info)
        self.file_list.itemSelectionChanged.connect(self.update_buttons)

        # Безопасное подключение сигналов модели
        model = self.file_list.model()
        if model:
            model.rowsInserted.connect(self.update_info) # Обновление при добавлении
            model.rowsRemoved.connect(self.update_info)   # Обновление при удалении

        self.update_info()
        self.update_buttons()

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Выберите PDF файлы',
            '',
            'PDF файлы (*.pdf)'
        )

        # Добавляем только уникальные файлы
        existing_files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                existing_files.append(item.text())
        for file_path in files:
            if file_path and file_path not in existing_files:
                self.file_list.addItem(file_path)

        # Обновление информации происходит через сигнал rowsInserted

    def remove_file(self):
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            self.file_list.takeItem(current_row)
            # Обновление информации происходит через сигнал rowsRemoved

    def clear_list(self):
        if self.file_list.count() > 0:
            reply = QMessageBox.question(
                self,
                'Подтверждение',
                'Очистить весь список файлов?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.file_list.clear()
                # Обновление информации происходит через сигнал rowsRemoved

    def move_up(self):
        current_row = self.file_list.currentRow()
        if current_row > 0:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row - 1, item)
            self.file_list.setCurrentRow(current_row - 1)
            self.update_buttons() # Обновить состояние кнопок после перемещения

    def move_down(self):
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1 and current_row >= 0:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row + 1, item)
            self.file_list.setCurrentRow(current_row + 1)
            self.update_buttons() # Обновить состояние кнопок после перемещения

    def update_info(self):
        count = self.file_list.count()

        # Обновляем счетчик файлов
        self.file_count_label.setText(f'Файлов: {count}')

        # Обновляем статус
        if not hasattr(self, 'worker') or not (self.worker and self.worker.isRunning()):
            if count == 0:
                self.status_label.setText('Добавьте PDF файлы для начала работы')
                self.status_icon.setPixmap(qta.icon('fa5s.info-circle', color='#17a2b8').pixmap(16, 16))
            elif count == 1:
                self.status_label.setText('Добавьте еще файлы для объединения')
                self.status_icon.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#ffc107').pixmap(16, 16))
            else:
                self.status_label.setText('Готов к объединению')
                self.status_icon.setPixmap(qta.icon('fa5s.check-circle', color='#28a745').pixmap(16, 16))

    def update_buttons(self):
        current_row = self.file_list.currentRow()
        count = self.file_list.count()
        is_merging = hasattr(self, 'worker') and self.worker is not None and self.worker.isRunning()

        self.add_btn.setEnabled(not is_merging)
        self.remove_btn.setEnabled(current_row >= 0 and not is_merging)
        self.clear_btn.setEnabled(count > 0 and not is_merging)
        self.preview_btn.setEnabled(current_row >= 0 and not is_merging) # Активируем кнопку просмотра только если выбран файл
        self.move_up_btn.setEnabled(current_row > 0 and not is_merging)
        self.move_down_btn.setEnabled(current_row >= 0 and current_row < count - 1 and not is_merging)
        self.merge_btn.setEnabled(count >= 2 and not is_merging)
        self.preview_all_btn.setEnabled(count >= 1 and not is_merging) # Активируем кнопку предпросмотра всех файлов

    def merge_pdfs(self):
        file_paths = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                file_paths.append(item.text())

        if len(file_paths) < 2:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Добавьте минимум 2 PDF файла для объединения'
            )
            return

        # Проверка существования файлов
        missing_files = [os.path.basename(f) for f in file_paths if not os.path.exists(f)]
        if missing_files:
            QMessageBox.warning(
                self,
                'Ошибка',
                f'Следующие файлы не найдены:\n{", ".join(missing_files)}'
            )
            return

        # Выбор места сохранения
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить объединенный PDF',
            'merged.pdf',
            'PDF файлы (*.pdf)'
        )

        if not output_file:
            return

        # Запускаем рабочий поток
        self.worker = PDFMergerWorker(file_paths, output_file)
        self.worker.finished.connect(self.merging_finished)
        self.worker.error.connect(self.merging_error)
        self.worker.started.connect(self.merging_started)
        self.worker.start()

    def merging_started(self):
        """Слот, вызываемый при начале объединения."""
        self.status_label.setText("Объединение файлов...")
        self.status_icon.setPixmap(qta.icon('fa5s.spinner', color='#17a2b8').pixmap(16, 16))
        self.update_buttons() # Деактивируем кнопки

    def merging_finished(self, output_file):
        """Слот, вызываемый при успешном завершении объединения."""
        self.worker = None # Очищаем ссылку на поток
        self.status_label.setText("Объединение завершено успешно!")
        self.status_icon.setPixmap(qta.icon('fa5s.check-circle', color='#28a745').pixmap(16, 16))
        self.update_buttons() # Активируем кнопки

        # Улучшенное сообщение об успехе
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle('Успешно!')
        msg.setText('PDF файлы успешно объединены!')
        msg.setInformativeText(f'Результат сохранен в:\n{output_file}')
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def merging_error(self, error_message):
        """Слот, вызываемый при ошибке объединения."""
        self.worker = None # Очищаем ссылку на поток
        self.status_label.setText("Ошибка при объединении")
        self.status_icon.setPixmap(qta.icon('fa5s.exclamation-circle', color='#dc3545').pixmap(16, 16))
        self.update_buttons() # Активируем кнопки

        # Улучшенное сообщение об ошибке
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle('Ошибка')
        msg.setText('Произошла ошибка при объединении файлов')
        msg.setInformativeText(error_message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def preview_pdf(self):
        """Открыть окно предварительного просмотра для выбранного PDF файла"""
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            item = self.file_list.item(current_row)
            if item:
                file_path = item.text()

                if not os.path.exists(file_path):
                    QMessageBox.warning(
                        self,
                        'Ошибка',
                        f'Файл не найден: {os.path.basename(file_path)}'
                    )
                    return

                if not fitz:
                    QMessageBox.warning(
                        self,
                        'Отсутствует зависимость',
                        'Для предварительного просмотра необходимо установить PyMuPDF:\npip install PyMuPDF'
                    )
                    return

                # Открываем окно предварительного просмотра
                preview_dialog = PDFPreviewDialog(self, file_path)
                preview_dialog.exec()

    def preview_all_pdfs(self):
        """Открыть окно предварительного просмотра всех PDF файлов перед объединением"""
        file_paths = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                file_paths.append(item.text())

        if not file_paths:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Добавьте PDF файлы для предварительного просмотра'
            )
            return

        if not fitz:
            QMessageBox.warning(
                self,
                'Отсутствует зависимость',
                'Для предварительного просмотра необходимо установить PyMuPDF:\npip install PyMuPDF'
            )
            return

        # Открываем окно предварительного просмотра всех файлов
        preview_all_dialog = PDFMultiPreviewDialog(self, file_paths)
        preview_all_dialog.exec()


class PDFPreviewDialog(QDialog):
    """Диалог для предварительного просмотра PDF-файлов"""

    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        self.file_path = file_path
        self.current_page = 0
        self.total_pages = 0
        self.doc = None
        self.zoom_factor = 1.0  # Начальный масштаб

        self.init_ui()
        if file_path and os.path.exists(file_path):
            self.load_pdf(file_path)

    def init_ui(self):
        self.setWindowTitle('Предварительный просмотр PDF')
        # Адаптируем под низкие разрешения
        self.setGeometry(100, 30, 750, 650)
        self.setMinimumSize(650, 500)
        self.setMaximumSize(950, 750)

        # Современный дизайн для диалога предпросмотра
        self.setStyleSheet("""
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
        """)

        # Компактный макет
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 10, 12, 10)

        # Компактная панель управления в две строки
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(4)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Первая строка - навигация по страницам
        nav_panel = QHBoxLayout()
        nav_panel.setSpacing(8)

        # Кнопки навигации по страницам
        self.prev_btn = QToolButton()
        self.prev_btn.setIcon(qta.icon('fa5s.chevron-left'))
        self.prev_btn.setToolTip('Предыдущая страница')
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setFixedSize(32, 32)
        nav_panel.addWidget(self.prev_btn)

        # Отображение текущей/всего страниц
        self.page_label = QLabel('Страница: 0 / 0')
        self.page_label.setObjectName('page_display')
        self.page_label.setMinimumWidth(120)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_panel.addWidget(self.page_label)

        self.next_btn = QToolButton()
        self.next_btn.setIcon(qta.icon('fa5s.chevron-right'))
        self.next_btn.setToolTip('Следующая страница')
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setFixedSize(32, 32)
        nav_panel.addWidget(self.next_btn)

        nav_panel.addStretch()
        controls_layout.addLayout(nav_panel)

        # Вторая строка - масштабирование
        zoom_panel = QHBoxLayout()
        zoom_panel.setSpacing(8)

        # Выбор масштаба
        zoom_label = QLabel('Масштаб:')
        zoom_panel.addWidget(zoom_label)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(['50%', '75%', '100%', '125%', '150%', '200%'])
        self.zoom_combo.setCurrentText('100%')
        self.zoom_combo.currentTextChanged.connect(self.change_zoom)
        self.zoom_combo.setMinimumWidth(80)
        zoom_panel.addWidget(self.zoom_combo)

        # Кнопки масштабирования
        self.zoom_out_btn = QToolButton()
        self.zoom_out_btn.setIcon(qta.icon('fa5s.search-minus'))
        self.zoom_out_btn.setToolTip('Уменьшить')
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setFixedSize(32, 32)
        zoom_panel.addWidget(self.zoom_out_btn)

        self.zoom_in_btn = QToolButton()
        self.zoom_in_btn.setIcon(qta.icon('fa5s.search-plus'))
        self.zoom_in_btn.setToolTip('Увеличить')
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setFixedSize(32, 32)
        zoom_panel.addWidget(self.zoom_in_btn)

        zoom_panel.addStretch()
        controls_layout.addLayout(zoom_panel)

        main_layout.addWidget(controls_widget)

        # Область просмотра
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Важно: False для правильной прокрутки больших страниц
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Метка для отображения изображения (без контейнера)
        self.preview_label = QLabel('Выберите PDF файл для просмотра')
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white;")

        # Устанавливаем метку как виджет для прокрутки
        self.scroll_area.setWidget(self.preview_label)

        # Добавляем область прокрутки в основной макет
        main_layout.addWidget(self.scroll_area, 1)

        # Нижняя панель с кнопками
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()

        # Кнопка закрытия
        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.close)
        bottom_panel.addWidget(close_btn)

        main_layout.addLayout(bottom_panel)

        # Начальное состояние кнопок
        self.update_navigation_buttons()

    def load_pdf(self, file_path):
        """Загрузить PDF файл для просмотра"""
        if not fitz:
            self.preview_label.setText("PyMuPDF не установлен.\nУстановите библиотеку: pip install PyMuPDF")
            return

        try:
            self.file_path = file_path
            self.doc = fitz.open(file_path)  # type: ignore
            self.total_pages = len(self.doc)
            self.current_page = 0

            # Обновляем информацию о страницах
            self.page_label.setText(f'Страница: {self.current_page + 1} / {self.total_pages}')

            # Отображаем первую страницу
            self.display_page(self.current_page)

            # Обновляем состояние кнопок навигации
            self.update_navigation_buttons()

            # Обновляем заголовок с именем файла
            self.setWindowTitle(f'Просмотр: {os.path.basename(file_path)}')
        except Exception as e:
            self.preview_label.setText(f"Ошибка при загрузке PDF: {str(e)}")

    def display_page(self, page_num):
        """Отобразить указанную страницу PDF"""
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return

        try:
            # Получаем страницу
            page = self.doc[page_num]

            # Устанавливаем масштаб
            zoom = self.zoom_factor

            # Рендерим страницу
            if fitz:  # Проверяем, что fitz импортирован успешно
                # type: ignore - игнорирование проверки типов для PyMuPDF
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))  # type: ignore
            else:
                return

            # Преобразуем в QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

            # Преобразуем в QPixmap и отображаем
            pixmap = QPixmap.fromImage(img)
            self.preview_label.setPixmap(pixmap)

            # Изменяем размер метки в соответствии с размером изображения
            self.preview_label.resize(pixmap.size())

            # Обновляем информацию о текущей странице
            self.page_label.setText(f'Страница: {page_num + 1} / {self.total_pages}')

            # Обновляем состояние кнопок навигации
            self.update_navigation_buttons()
        except Exception as e:
            self.preview_label.setText(f"Ошибка при отображении страницы: {str(e)}")

    def prev_page(self):
        """Перейти к предыдущей странице"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)

    def next_page(self):
        """Перейти к следующей странице"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page(self.current_page)

    def update_navigation_buttons(self):
        """Обновить состояние кнопок навигации"""
        has_doc = self.doc is not None and self.total_pages > 0

        self.prev_btn.setEnabled(has_doc and self.current_page > 0)
        self.next_btn.setEnabled(has_doc and self.current_page < self.total_pages - 1)
        self.zoom_combo.setEnabled(has_doc)
        self.zoom_in_btn.setEnabled(has_doc)
        self.zoom_out_btn.setEnabled(has_doc)

    def change_zoom(self, zoom_text):
        """Изменить масштаб отображения"""
        try:
            # Получаем числовое значение масштаба из текста (например, из "100%")
            zoom_value = float(zoom_text.rstrip('%')) / 100.0
            self.zoom_factor = zoom_value

            # Перерисовываем текущую страницу с новым масштабом
            if self.doc:
                self.display_page(self.current_page)
        except ValueError:
            pass

    def zoom_in(self):
        """Увеличить масштаб"""
        # Находим следующий больший масштаб в комбобоксе
        current_index = self.zoom_combo.currentIndex()
        if current_index < self.zoom_combo.count() - 1:
            self.zoom_combo.setCurrentIndex(current_index + 1)

    def zoom_out(self):
        """Уменьшить масштаб"""
        # Находим следующий меньший масштаб в комбобоксе
        current_index = self.zoom_combo.currentIndex()
        if current_index > 0:
            self.zoom_combo.setCurrentIndex(current_index - 1)

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        # Закрываем документ при закрытии окна
        if self.doc:
            self.doc.close()  # type: ignore
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Установка иконки приложения
    app.setWindowIcon(qta.icon('fa5s.file-pdf'))

    window = PDFMergerApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
