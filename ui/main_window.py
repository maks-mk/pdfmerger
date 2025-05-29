"""
Главное окно приложения PDF Merger Pro
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QFileDialog, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import qtawesome as qta

from .widgets import PDFListWidget, StatusWidget, FileCountWidget, CompactButton
from .styles import APP_STYLES
from .preview_dialogs import PDFPreviewDialog, MultiPreviewDialog
from core.pdf_worker import PDFMergerWorker, PDFValidator, PDFInfo
from core.file_converter import FileConverter


class PDFMergerMainWindow(QMainWindow):
    """Главное окно приложения PDF Merger Pro."""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.file_converter = FileConverter()
        self.temp_files = []  # Список временных файлов для очистки
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle('PDF Merger Pro')
        self.setGeometry(50, 30, 650, 600)
        self.setMinimumSize(600, 500)
        self.setMaximumSize(800, 700)
        self.setStyleSheet(APP_STYLES)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Компактный layout для низких разрешений
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 12, 16, 12)

        # Создаем элементы интерфейса
        self.create_header(main_layout)
        self.create_file_list(main_layout)
        self.create_file_controls(main_layout)
        self.create_action_controls(main_layout)
        self.create_status_bar(main_layout)

    def create_header(self, main_layout):
        """Создает заголовок приложения."""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Компактная иконка
        icon_label = QLabel()
        icon_size = 32
        qt_icon = qta.icon('fa5s.file-pdf', color='#667eea')
        icon_pixmap = qt_icon.pixmap(icon_size, icon_size)
        icon_label.setPixmap(icon_pixmap)
        header_layout.addWidget(icon_label)

        # Заголовок
        title_label = QLabel('PDF Merger Pro')
        title_label.setObjectName('title')
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Информация о версии
        version_label = QLabel('v2.2')
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

        # Подзаголовок
        subtitle_label = QLabel('Перетащите файлы (PDF, Word, изображения, текст) в область ниже или используйте кнопки')
        subtitle_label.setObjectName('subtitle')
        main_layout.addWidget(subtitle_label)

    def create_file_list(self, main_layout):
        """Создает список файлов."""
        self.file_list = PDFListWidget()
        self.file_list.setMinimumHeight(180)
        self.file_list.setMaximumHeight(250)
        self.file_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(self.file_list)

    def create_file_controls(self, main_layout):
        """Создает элементы управления файлами."""
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

        # Кнопка добавления
        self.add_btn = CompactButton.create_button(
            'Добавить файлы', 'fa5s.plus', '#28a745', 'success'
        )
        self.add_btn.clicked.connect(self.add_files)
        main_controls_layout.addWidget(self.add_btn)

        # Кнопка предварительного просмотра
        self.preview_btn = CompactButton.create_button(
            'Просмотр', 'fa5s.eye', '#17a2b8', 'info'
        )
        self.preview_btn.clicked.connect(self.preview_pdf)
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
        self.remove_btn = CompactButton.create_button(
            'Удалить выбранный', 'fa5s.trash', '#dc3545', 'danger'
        )
        self.remove_btn.clicked.connect(self.remove_file)
        secondary_controls_layout.addWidget(self.remove_btn)

        # Кнопка очистки
        self.clear_btn = CompactButton.create_button(
            'Очистить все', 'fa5s.broom', '#856404', 'warning'
        )
        self.clear_btn.clicked.connect(self.clear_list)
        secondary_controls_layout.addWidget(self.clear_btn)

        secondary_controls_layout.addStretch()
        file_controls_layout.addLayout(secondary_controls_layout)

        main_layout.addWidget(file_controls_group)

    def create_action_controls(self, main_layout):
        """Создает элементы основных действий."""
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

    def create_status_bar(self, main_layout):
        """Создает панель статуса."""
        status_group = QWidget()
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(12)

        # Иконка статуса
        self.status_icon = QLabel()
        status_icon_pixmap = qta.icon('fa5s.check-circle', color='#28a745').pixmap(16, 16)
        self.status_icon.setPixmap(status_icon_pixmap)
        status_layout.addWidget(self.status_icon)

        # Виджет статуса
        self.status_widget = StatusWidget()
        status_layout.addWidget(self.status_widget)

        status_layout.addStretch()

        # Счетчик файлов
        self.file_count_widget = FileCountWidget()
        status_layout.addWidget(self.file_count_widget)

        main_layout.addWidget(status_group)

    def setup_connections(self):
        """Настройка соединений сигналов."""
        # Обновление информации при изменении списка
        self.file_list.itemChanged.connect(self.update_info)
        self.file_list.itemSelectionChanged.connect(self.update_buttons)

        # Безопасное подключение сигналов модели
        model = self.file_list.model()
        if model:
            model.rowsInserted.connect(self.update_info)
            model.rowsRemoved.connect(self.update_info)

        # Начальное обновление
        self.update_info()
        self.update_buttons()

    def add_files(self):
        """Добавить файлы различных форматов."""
        # Используем новый фильтр файлов с поддержкой различных форматов
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Выберите файлы для объединения',
            '',
            FileConverter.get_file_filter()
        )

        if files:
            # Получаем существующие файлы
            existing_files = []
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                if item:
                    existing_files.append(item.text())

            # Добавляем только новые файлы
            added_count = 0
            converted_count = 0

            for file_path in files:
                if file_path not in existing_files:
                    # Проверяем поддержку формата
                    if not FileConverter.is_supported_format(file_path):
                        QMessageBox.warning(
                            self,
                            'Неподдерживаемый формат',
                            f'Файл {os.path.basename(file_path)} имеет неподдерживаемый формат'
                        )
                        continue

                    # Конвертируем файл в PDF если нужно
                    success, result = self.file_converter.convert_to_pdf(file_path)

                    if success:
                        pdf_path = result

                        # Если файл был сконвертирован (не оригинальный PDF)
                        if pdf_path != file_path:
                            converted_count += 1
                            self.temp_files.append(pdf_path)

                        # Валидируем получившийся PDF
                        is_valid, message = PDFValidator.is_valid_pdf(pdf_path)
                        if is_valid:
                            # Добавляем оригинальный путь в список (для отображения)
                            # но сохраняем путь к PDF для объединения
                            self.file_list.addItem(file_path)
                            added_count += 1
                        else:
                            QMessageBox.warning(
                                self,
                                'Ошибка файла',
                                f'Файл {os.path.basename(file_path)}:\n{message}'
                            )
                            # Удаляем временный файл если он был создан
                            if pdf_path != file_path and pdf_path in self.temp_files:
                                self.temp_files.remove(pdf_path)
                                try:
                                    os.remove(pdf_path)
                                except Exception:
                                    pass
                    else:
                        # Ошибка конвертации
                        error_message = result
                        QMessageBox.warning(
                            self,
                            'Ошибка конвертации',
                            f'Не удалось обработать файл {os.path.basename(file_path)}:\n{error_message}'
                        )

            # Показываем результат
            if added_count > 0:
                status_msg = f'Добавлено файлов: {added_count}'
                if converted_count > 0:
                    status_msg += f' (сконвертировано: {converted_count})'
                self.status_widget.set_status(status_msg, 'success')

                # Показываем информацию о недостающих зависимостях
                missing_deps = self.file_converter.get_missing_dependencies()
                if missing_deps and converted_count == 0:
                    QMessageBox.information(
                        self,
                        'Информация о зависимостях',
                        f'Для полной поддержки конвертации установите:\n' +
                        '\n'.join([f'• pip install {dep.split()[0].lower()}' for dep in missing_deps])
                    )

    def remove_file(self):
        """Удалить выбранный файл."""
        current_row = self.file_list.currentRow()
        if current_row >= 0:
            item = self.file_list.takeItem(current_row)
            if item:
                self.status_widget.set_status(f'Удален файл: {os.path.basename(item.text())}', 'info')

    def clear_list(self):
        """Очистить список файлов."""
        if self.file_list.count() > 0:
            reply = QMessageBox.question(
                self,
                'Подтверждение',
                'Удалить все файлы из списка?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                count = self.file_list.count()
                self.file_list.clear()
                self.status_widget.set_status(f'Удалено файлов: {count}', 'info')

    def move_up(self):
        """Переместить файл вверх."""
        current_row = self.file_list.currentRow()
        if current_row > 0:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row - 1, item)
            self.file_list.setCurrentRow(current_row - 1)

    def move_down(self):
        """Переместить файл вниз."""
        current_row = self.file_list.currentRow()
        if current_row >= 0 and current_row < self.file_list.count() - 1:
            item = self.file_list.takeItem(current_row)
            self.file_list.insertItem(current_row + 1, item)
            self.file_list.setCurrentRow(current_row + 1)

    def preview_pdf(self):
        """Открыть окно предварительного просмотра для выбранного PDF файла."""
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

                # Открываем окно предварительного просмотра
                preview_dialog = PDFPreviewDialog(self, file_path)
                preview_dialog.exec()

    def preview_all_pdfs(self):
        """Открыть окно предварительного просмотра всех PDF файлов."""
        file_paths = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                file_paths.append(item.text())

        if not file_paths:
            QMessageBox.information(
                self,
                'Информация',
                'Добавьте PDF файлы для предварительного просмотра'
            )
            return

        # Проверяем наличие PyMuPDF
        try:
            import fitz
        except ImportError:
            QMessageBox.warning(
                self,
                'Отсутствует зависимость',
                'Для предварительного просмотра необходимо установить PyMuPDF:\npip install PyMuPDF'
            )
            return

        # Открываем мультипредпросмотр
        try:
            preview_dialog = MultiPreviewDialog(self, file_paths)
            preview_dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                'Ошибка предпросмотра',
                f'Не удалось открыть предпросмотр:\n{str(e)}'
            )

    def merge_pdfs(self):
        """Объединить PDF файлы."""
        original_paths = []
        pdf_paths = []

        # Получаем пути к файлам и их PDF версиям
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item:
                original_path = item.text()
                original_paths.append(original_path)

                # Если файл был сконвертирован, используем PDF версию
                if original_path.lower().endswith('.pdf'):
                    pdf_paths.append(original_path)
                else:
                    # Ищем соответствующий временный PDF файл
                    success, pdf_path = self.file_converter.convert_to_pdf(original_path)
                    if success:
                        pdf_paths.append(pdf_path)
                        # Добавляем в список временных файлов если еще нет
                        if pdf_path not in self.temp_files:
                            self.temp_files.append(pdf_path)
                    else:
                        QMessageBox.warning(
                            self,
                            'Ошибка конвертации',
                            f'Не удалось подготовить файл {os.path.basename(original_path)} для объединения'
                        )
                        return

        # Валидация PDF файлов
        is_valid, message = PDFValidator.validate_file_list(pdf_paths)
        if not is_valid:
            QMessageBox.warning(self, 'Ошибка валидации', message)
            return

        # Выбор места сохранения
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить объединенный PDF',
            'merged_document.pdf',
            'PDF файлы (*.pdf)'
        )

        if output_file:
            # Запускаем рабочий поток с PDF файлами
            self.worker = PDFMergerWorker(pdf_paths, output_file)
            self.worker.started.connect(self.merging_started)
            self.worker.finished.connect(self.merging_finished)
            self.worker.error.connect(self.merging_error)
            self.worker.start()

    def update_info(self):
        """Обновить информацию о файлах."""
        count = self.file_list.count()
        self.file_count_widget.update_count(count)

        # Обновляем статус
        if not hasattr(self, 'worker') or not (self.worker and self.worker.isRunning()):
            if count == 0:
                self.status_widget.set_status('Добавьте PDF файлы для начала работы', 'info')
                self.status_icon.setPixmap(qta.icon('fa5s.info-circle', color='#17a2b8').pixmap(16, 16))
            elif count == 1:
                self.status_widget.set_status('Добавьте еще файлы для объединения', 'warning')
                self.status_icon.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#ffc107').pixmap(16, 16))
            else:
                self.status_widget.set_status('Готов к объединению', 'success')
                self.status_icon.setPixmap(qta.icon('fa5s.check-circle', color='#28a745').pixmap(16, 16))

    def update_buttons(self):
        """Обновить состояние кнопок."""
        count = self.file_list.count()
        current_row = self.file_list.currentRow()
        has_selection = current_row >= 0
        is_working = hasattr(self, 'worker') and self.worker and self.worker.isRunning()

        # Кнопки управления файлами
        self.add_btn.setEnabled(not is_working)
        self.remove_btn.setEnabled(has_selection and not is_working)
        self.clear_btn.setEnabled(count > 0 and not is_working)
        self.move_up_btn.setEnabled(has_selection and current_row > 0 and not is_working)
        self.move_down_btn.setEnabled(has_selection and current_row < count - 1 and not is_working)

        # Кнопки действий
        self.preview_btn.setEnabled(has_selection and not is_working)
        self.preview_all_btn.setEnabled(count > 0 and not is_working)
        self.merge_btn.setEnabled(count >= 2 and not is_working)

    def merging_started(self):
        """Слот, вызываемый при начале объединения."""
        # Определяем, какая библиотека будет использоваться
        try:
            import fitz
            merge_method = "PyMuPDF (оптимально для кирилицы)"
        except ImportError:
            merge_method = "PyPDF2 (базовый)"

        self.status_widget.set_status(f"Объединение файлов ({merge_method})...", 'processing')
        self.status_icon.setPixmap(qta.icon('fa5s.spinner', color='#6f42c1').pixmap(16, 16))
        self.update_buttons()

    def merging_finished(self, output_file):
        """Слот, вызываемый при успешном завершении объединения."""
        self.worker = None
        self.status_widget.set_status("Объединение завершено успешно!", 'success')
        self.status_icon.setPixmap(qta.icon('fa5s.check-circle', color='#28a745').pixmap(16, 16))
        self.update_buttons()

        # Очищаем временные файлы
        self.cleanup_temp_files()

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
        self.worker = None
        self.status_widget.set_status("Ошибка при объединении", 'error')
        self.status_icon.setPixmap(qta.icon('fa5s.exclamation-circle', color='#dc3545').pixmap(16, 16))
        self.update_buttons()

        # Очищаем временные файлы
        self.cleanup_temp_files()

        # Улучшенное сообщение об ошибке
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle('Ошибка')
        msg.setText('Произошла ошибка при объединении файлов')
        msg.setInformativeText(error_message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def cleanup_temp_files(self):
        """Очищает временные файлы."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Не удалось удалить временный файл {temp_file}: {e}")

        self.temp_files.clear()
        self.file_converter.cleanup_temp_files()

    def closeEvent(self, event):
        """Обработчик закрытия приложения."""
        # Очищаем временные файлы при закрытии
        self.cleanup_temp_files()
        event.accept()
