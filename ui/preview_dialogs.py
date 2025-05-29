"""
Диалоги предпросмотра PDF файлов
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QComboBox, QToolButton, QPushButton,
                             QWidget, QSplitter, QListWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QFont
import qtawesome as qta
from .styles import DIALOG_STYLES

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class BasePDFPreviewDialog(QDialog):
    """Базовый класс для диалогов предпросмотра PDF."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.setStyleSheet(DIALOG_STYLES)

    def create_navigation_controls(self):
        """Создает элементы навигации."""
        # Кнопки навигации по страницам
        self.prev_btn = QToolButton()
        self.prev_btn.setIcon(qta.icon('fa5s.chevron-left'))
        self.prev_btn.setToolTip('Предыдущая страница')
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setFixedSize(32, 32)

        # Отображение текущей/всего страниц
        self.page_label = QLabel('Страница: 0 / 0')
        self.page_label.setObjectName('page_display')
        self.page_label.setMinimumWidth(120)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QToolButton()
        self.next_btn.setIcon(qta.icon('fa5s.chevron-right'))
        self.next_btn.setToolTip('Следующая страница')
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setFixedSize(32, 32)

    def create_zoom_controls(self):
        """Создает элементы масштабирования."""
        # Выбор масштаба
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(['50%', '75%', '100%', '125%', '150%', '200%'])
        self.zoom_combo.setCurrentText('100%')
        self.zoom_combo.currentTextChanged.connect(self.change_zoom)
        self.zoom_combo.setMinimumWidth(80)

        # Кнопки масштабирования
        self.zoom_out_btn = QToolButton()
        self.zoom_out_btn.setIcon(qta.icon('fa5s.search-minus'))
        self.zoom_out_btn.setToolTip('Уменьшить')
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.zoom_out_btn.setFixedSize(32, 32)

        self.zoom_in_btn = QToolButton()
        self.zoom_in_btn.setIcon(qta.icon('fa5s.search-plus'))
        self.zoom_in_btn.setToolTip('Увеличить')
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_in_btn.setFixedSize(32, 32)

    def create_preview_area(self):
        """Создает область предпросмотра."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.preview_label = QLabel('Выберите PDF файл для просмотра')
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white;")

        self.scroll_area.setWidget(self.preview_label)

    def display_page(self, page_num):
        """Отобразить указанную страницу PDF"""
        if not self.doc or page_num < 0 or page_num >= self.total_pages:
            return

        try:
            if not fitz:
                self.preview_label.setText("PyMuPDF не установлен")
                return

            # Получаем страницу
            page = self.doc[page_num]

            # Рендерим страницу с масштабом
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_factor, self.zoom_factor))

            # Преобразуем в QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

            # Преобразуем в QPixmap и отображаем
            pixmap = QPixmap.fromImage(img)
            self.preview_label.setPixmap(pixmap)
            self.preview_label.resize(pixmap.size())

            # Обновляем информацию о текущей странице
            self.page_label.setText(f'Страница: {page_num + 1} / {self.total_pages}')
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

    def change_zoom(self, zoom_text):
        """Изменить масштаб отображения"""
        try:
            zoom_value = float(zoom_text.rstrip('%')) / 100.0
            self.zoom_factor = zoom_value
            if self.doc:
                self.display_page(self.current_page)
        except ValueError:
            pass

    def zoom_in(self):
        """Увеличить масштаб"""
        current_index = self.zoom_combo.currentIndex()
        if current_index < self.zoom_combo.count() - 1:
            self.zoom_combo.setCurrentIndex(current_index + 1)

    def zoom_out(self):
        """Уменьшить масштаб"""
        current_index = self.zoom_combo.currentIndex()
        if current_index > 0:
            self.zoom_combo.setCurrentIndex(current_index - 1)

    def update_navigation_buttons(self):
        """Обновить состояние кнопок навигации"""
        has_doc = self.doc is not None and self.total_pages > 0

        self.prev_btn.setEnabled(has_doc and self.current_page > 0)
        self.next_btn.setEnabled(has_doc and self.current_page < self.total_pages - 1)
        self.zoom_combo.setEnabled(has_doc)
        self.zoom_in_btn.setEnabled(has_doc)
        self.zoom_out_btn.setEnabled(has_doc)

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.doc:
            self.doc.close()
        event.accept()


class PDFPreviewDialog(BasePDFPreviewDialog):
    """Диалог предпросмотра одного PDF файла."""

    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        self.file_path = file_path
        self.init_ui()
        if file_path:
            self.load_pdf(file_path)

    def init_ui(self):
        self.setWindowTitle('Предварительный просмотр PDF')
        self.setGeometry(100, 30, 750, 690)
        self.setMinimumSize(650, 500)
        self.setMaximumSize(950, 750)

        # Компактный макет
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 10, 12, 10)

        # Создаем элементы управления
        self.create_navigation_controls()
        self.create_zoom_controls()
        self.create_preview_area()

        # Компактная панель управления в две строки
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(4)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # Первая строка - навигация по страницам
        nav_panel = QHBoxLayout()
        nav_panel.setSpacing(8)
        nav_panel.addWidget(self.prev_btn)
        nav_panel.addWidget(self.page_label)
        nav_panel.addWidget(self.next_btn)
        nav_panel.addStretch()
        controls_layout.addLayout(nav_panel)

        # Вторая строка - масштабирование
        zoom_panel = QHBoxLayout()
        zoom_panel.setSpacing(8)
        zoom_panel.addWidget(QLabel('Масштаб:'))
        zoom_panel.addWidget(self.zoom_combo)
        zoom_panel.addWidget(self.zoom_out_btn)
        zoom_panel.addWidget(self.zoom_in_btn)
        zoom_panel.addStretch()
        controls_layout.addLayout(zoom_panel)

        main_layout.addWidget(controls_widget)
        main_layout.addWidget(self.scroll_area, 1)

        # Нижняя панель с кнопками
        bottom_panel = QHBoxLayout()
        bottom_panel.addStretch()
        close_btn = QPushButton('Закрыть')
        close_btn.clicked.connect(self.close)
        bottom_panel.addWidget(close_btn)
        main_layout.addLayout(bottom_panel)

        self.update_navigation_buttons()

        # Горячие клавиши для одиночного предпросмотра
        self.setup_single_shortcuts()

    def setup_single_shortcuts(self):
        """Настройка горячих клавиш для одиночного предпросмотра"""
        # Навигация по страницам
        QShortcut(QKeySequence("Left"), self, self.prev_page)
        QShortcut(QKeySequence("Right"), self, self.next_page)
        QShortcut(QKeySequence("Up"), self, self.prev_page)
        QShortcut(QKeySequence("Down"), self, self.next_page)

        # Масштабирование
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.reset_zoom_single)

        # Закрытие
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)

    def reset_zoom_single(self):
        """Сбросить масштаб к 100% для одиночного предпросмотра"""
        self.zoom_combo.setCurrentText('100%')

    def load_pdf(self, file_path):
        """Загрузить PDF файл для просмотра"""
        if not fitz:
            self.preview_label.setText("PyMuPDF не установлен.\nУстановите библиотеку: pip install PyMuPDF")
            return

        try:
            self.file_path = file_path
            self.doc = fitz.open(file_path)
            self.total_pages = len(self.doc)
            self.current_page = 0

            self.page_label.setText(f'Страница: {self.current_page + 1} / {self.total_pages}')
            self.display_page(self.current_page)
            self.update_navigation_buttons()
            self.setWindowTitle(f'Просмотр: {os.path.basename(file_path)}')

        except Exception as e:
            self.preview_label.setText(f"Ошибка при загрузке PDF: {str(e)}")


class MultiPreviewDialog(BasePDFPreviewDialog):
    """Диалог предпросмотра нескольких PDF файлов."""

    def __init__(self, parent=None, file_paths=None):
        super().__init__(parent)
        self.file_paths = file_paths or []
        self.current_file_index = 0
        self.init_ui()
        if self.file_paths:
            self.load_current_file()

    def init_ui(self):
        self.setWindowTitle('Предпросмотр всех файлов')
        # Адаптируем под низкие разрешения
        self.setGeometry(50, 30, 900, 690)
        self.setMinimumSize(800, 550)
        self.setMaximumSize(1100, 750)

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

        # Основной разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - список файлов
        file_panel = QWidget()
        file_layout = QVBoxLayout(file_panel)
        file_layout.setContentsMargins(0, 0, 10, 0)

        # Заголовок списка файлов
        file_list_label = QLabel('Файлы для объединения:')
        file_list_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        file_layout.addWidget(file_list_label)

        # Статистика файлов
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            color: #666;
            font-size: 11px;
            padding: 4px 8px;
            background-color: #f0f0f0;
            border-radius: 4px;
            margin-bottom: 5px;
        """)
        self.update_stats()
        file_layout.addWidget(self.stats_label)

        # Список файлов
        self.file_list_widget = QListWidget()
        self.file_list_widget.setMaximumWidth(250)
        self.file_list_widget.setMinimumWidth(200)

        # Заполняем список файлов с дополнительной информацией
        for i, file_path in enumerate(self.file_paths):
            item_text = self.get_file_display_name(file_path, i)
            self.file_list_widget.addItem(item_text)

        # Подключаем сигнал выбора файла
        self.file_list_widget.currentRowChanged.connect(self.change_file)

        file_layout.addWidget(self.file_list_widget, 1)
        splitter.addWidget(file_panel)

        # Правая панель - просмотр PDF
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(10, 0, 0, 0)

        # Создаем элементы управления
        self.create_navigation_controls()
        self.create_zoom_controls()
        self.create_preview_area()

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

        nav_panel.addWidget(self.prev_btn)
        nav_panel.addWidget(self.page_label)
        nav_panel.addWidget(self.next_btn)
        nav_panel.addStretch()

        # Выбор масштаба
        zoom_label = QLabel('Масштаб:')
        zoom_label.setStyleSheet("font-size: 11px;")
        nav_panel.addWidget(zoom_label)
        nav_panel.addWidget(self.zoom_combo)

        controls_layout.addLayout(nav_panel)
        preview_layout.addWidget(controls_widget)
        preview_layout.addWidget(self.scroll_area, 1)

        splitter.addWidget(preview_panel)

        # Устанавливаем соотношение разделителя
        splitter.setSizes([200, 700])  # Примерное соотношение сторон

        main_layout.addWidget(splitter, 1)

        # Нижняя панель с кнопками навигации по файлам
        bottom_panel = QHBoxLayout()

        self.prev_file_btn = QPushButton('◀ Предыдущий файл')
        self.prev_file_btn.setIcon(qta.icon('fa5s.file-pdf'))
        self.prev_file_btn.clicked.connect(self.prev_file)
        bottom_panel.addWidget(self.prev_file_btn)

        bottom_panel.addStretch()

        self.next_file_btn = QPushButton('Следующий файл ▶')
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

        # Горячие клавиши
        self.setup_shortcuts()

    def load_current_file(self):
        """Загрузить текущий PDF файл для просмотра"""
        # Закрываем предыдущий документ, если он открыт
        if self.doc:
            self.doc.close()
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

            self.doc = fitz.open(file_path)
            self.current_page = 0
            self.total_pages = len(self.doc)

            # Обновляем информацию о файле и страницах
            self.file_info_label.setText(f'Файл: {os.path.basename(file_path)}')
            self.page_label.setText(f'Страница: 1 / {self.total_pages}')

            # Выделяем текущий файл в списке
            self.file_list_widget.setCurrentRow(self.current_file_index)

            # Отображаем первую страницу
            self.display_page(self.current_page)

            # Обновляем состояние кнопок навигации
            self.update_navigation()
        except Exception as e:
            self.preview_label.setText(f"Ошибка при загрузке PDF: {str(e)}")
            self.update_navigation()

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

    def update_stats(self):
        """Обновить статистику файлов"""
        if not self.file_paths:
            self.stats_label.setText("Нет файлов")
            return

        try:
            from core.pdf_worker import PDFInfo

            total_files = len(self.file_paths)
            total_pages = 0
            total_size = 0
            valid_files = 0

            for file_path in self.file_paths:
                if os.path.exists(file_path):
                    valid_files += 1
                    info = PDFInfo.get_file_info(file_path)
                    total_pages += info['pages']
                    total_size += info['size']

            size_mb = round(total_size / (1024 * 1024), 1)

            stats_text = f"Файлов: {valid_files}/{total_files}\n"
            stats_text += f"Страниц: {total_pages}\n"
            stats_text += f"Размер: {size_mb} МБ"

            self.stats_label.setText(stats_text)

        except Exception:
            self.stats_label.setText(f"Файлов: {len(self.file_paths)}")

    def get_file_display_name(self, file_path, index):
        """Получить отображаемое имя файла с дополнительной информацией"""
        try:
            from core.pdf_worker import PDFInfo

            base_name = os.path.basename(file_path)
            if not os.path.exists(file_path):
                return f"{index+1}. {base_name} ❌"

            info = PDFInfo.get_file_info(file_path)
            if info['pages'] > 0:
                return f"{index+1}. {base_name} ({info['pages']} стр.)"
            else:
                return f"{index+1}. {base_name} ⚠️"

        except Exception:
            return f"{index+1}. {os.path.basename(file_path)}"

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # Навигация по страницам
        QShortcut(QKeySequence("Left"), self, self.prev_page)
        QShortcut(QKeySequence("Right"), self, self.next_page)
        QShortcut(QKeySequence("Up"), self, self.prev_page)
        QShortcut(QKeySequence("Down"), self, self.next_page)

        # Навигация по файлам
        QShortcut(QKeySequence("Ctrl+Left"), self, self.prev_file)
        QShortcut(QKeySequence("Ctrl+Right"), self, self.next_file)
        QShortcut(QKeySequence("Ctrl+Up"), self, self.prev_file)
        QShortcut(QKeySequence("Ctrl+Down"), self, self.next_file)

        # Масштабирование
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.reset_zoom)

        # Закрытие
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)

    def reset_zoom(self):
        """Сбросить масштаб к 100%"""
        self.zoom_combo.setCurrentText('100%')
