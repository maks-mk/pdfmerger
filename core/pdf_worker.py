"""
Рабочий поток для объединения PDF файлов
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    print("PyPDF2 не установлен")
    PdfReader = PdfWriter = None
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    print("PyMuPDF не установлен")
    fitz = None
    PYMUPDF_AVAILABLE = False


class PDFMergerWorker(QThread):
    """Рабочий поток для объединения PDF файлов."""

    # Сигналы
    finished = pyqtSignal(str)  # Сигнал завершения с путем к файлу
    error = pyqtSignal(str)     # Сигнал ошибки с сообщением
    started = pyqtSignal()      # Сигнал начала работы

    def __init__(self, file_paths, output_path):
        super().__init__()
        self.file_paths = file_paths
        self.output_path = output_path

    def run(self):
        """Основной метод выполнения объединения PDF."""
        try:
            self.started.emit()

            # Используем PyMuPDF если доступен (лучше работает с кириллицей)
            if PYMUPDF_AVAILABLE:
                success = self._merge_with_pymupdf()
            elif PYPDF2_AVAILABLE:
                success = self._merge_with_pypdf2()
            else:
                self.error.emit("Ни PyMuPDF, ни PyPDF2 не установлены")
                return

            if success:
                self.finished.emit(self.output_path)

        except Exception as e:
            self.error.emit(f"Неожиданная ошибка: {str(e)}")

    def _merge_with_pymupdf(self):
        """Объединение PDF с использованием PyMuPDF (лучше для кирилицы)."""
        try:
            if not fitz:
                self.error.emit("PyMuPDF не доступен")
                return False

            # Создаем новый PDF документ
            merged_doc = fitz.open()

            # Проходим по всем файлам
            for file_path in self.file_paths:
                if not os.path.exists(file_path):
                    self.error.emit(f"Файл не найден: {file_path}")
                    return False

                try:
                    # Открываем PDF файл
                    doc = fitz.open(file_path)

                    # Добавляем все страницы
                    merged_doc.insert_pdf(doc)

                    # Закрываем документ
                    doc.close()

                except Exception as e:
                    self.error.emit(f"Ошибка при чтении файла {os.path.basename(file_path)}: {str(e)}")
                    return False

            # Проверяем, что есть страницы
            if merged_doc.page_count == 0:
                self.error.emit("Нет страниц для объединения")
                merged_doc.close()
                return False

            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

            # Сохраняем объединенный PDF
            merged_doc.save(self.output_path)
            merged_doc.close()

            # Проверяем, что файл создан
            if not os.path.exists(self.output_path):
                self.error.emit("Не удалось создать выходной файл")
                return False

            return True

        except Exception as e:
            self.error.emit(f"Ошибка PyMuPDF: {str(e)}")
            return False

    def _merge_with_pypdf2(self):
        """Объединение PDF с использованием PyPDF2 (fallback)."""
        try:
            if not PdfWriter or not PdfReader:
                self.error.emit("PyPDF2 не установлен")
                return False

            # Создаем объект для записи
            pdf_writer = PdfWriter()

            # Проходим по всем файлам
            for file_path in self.file_paths:
                if not os.path.exists(file_path):
                    self.error.emit(f"Файл не найден: {file_path}")
                    return False

                try:
                    # Читаем PDF файл
                    pdf_reader = PdfReader(file_path)

                    # Добавляем все страницы в writer
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                except Exception as e:
                    self.error.emit(f"Ошибка при чтении файла {os.path.basename(file_path)}: {str(e)}")
                    return False

            # Проверяем, что есть страницы для записи
            if len(pdf_writer.pages) == 0:
                self.error.emit("Нет страниц для объединения")
                return False

            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

            # Записываем объединенный PDF
            with open(self.output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            # Проверяем, что файл создан
            if not os.path.exists(self.output_path):
                self.error.emit("Не удалось создать выходной файл")
                return False

            return True

        except Exception as e:
            self.error.emit(f"Ошибка PyPDF2: {str(e)}")
            return False


class PDFValidator:
    """Класс для валидации PDF файлов."""

    @staticmethod
    def is_valid_pdf(file_path):
        """Проверяет, является ли файл валидным PDF."""
        if not os.path.exists(file_path):
            return False, "Файл не существует"

        if not file_path.lower().endswith('.pdf'):
            return False, "Файл не является PDF"

        # Пробуем PyMuPDF сначала (лучше работает с кириллицей)
        if PYMUPDF_AVAILABLE and fitz:
            try:
                doc = fitz.open(file_path)
                page_count = doc.page_count
                doc.close()

                if page_count == 0:
                    return False, "PDF файл пустой"
                return True, "OK"
            except Exception as e:
                # Если PyMuPDF не смог, пробуем PyPDF2
                pass

        # Fallback на PyPDF2
        if PYPDF2_AVAILABLE and PdfReader:
            try:
                reader = PdfReader(file_path)
                # Проверяем, что есть хотя бы одна страница
                if len(reader.pages) == 0:
                    return False, "PDF файл пустой"
                return True, "OK"
            except Exception as e:
                return False, f"Ошибка чтения PDF: {str(e)}"

        return False, "Ни PyMuPDF, ни PyPDF2 не установлены"

    @staticmethod
    def validate_file_list(file_paths):
        """Валидирует список PDF файлов."""
        if not file_paths:
            return False, "Список файлов пуст"

        if len(file_paths) < 2:
            return False, "Для объединения нужно минимум 2 файла"

        for file_path in file_paths:
            is_valid, message = PDFValidator.is_valid_pdf(file_path)
            if not is_valid:
                return False, f"Файл {os.path.basename(file_path)}: {message}"

        return True, "Все файлы валидны"


class PDFInfo:
    """Класс для получения информации о PDF файлах."""

    @staticmethod
    def get_page_count(file_path):
        """Возвращает количество страниц в PDF файле."""
        if not os.path.exists(file_path):
            return 0

        # Пробуем PyMuPDF сначала
        if PYMUPDF_AVAILABLE and fitz:
            try:
                doc = fitz.open(file_path)
                page_count = doc.page_count
                doc.close()
                return page_count
            except Exception:
                pass

        # Fallback на PyPDF2
        if PYPDF2_AVAILABLE and PdfReader:
            try:
                reader = PdfReader(file_path)
                return len(reader.pages)
            except Exception:
                pass

        return 0

    @staticmethod
    def get_file_info(file_path):
        """Возвращает информацию о PDF файле."""
        if not os.path.exists(file_path):
            return {
                'name': os.path.basename(file_path),
                'size': 0,
                'pages': 0,
                'exists': False
            }

        try:
            file_size = os.path.getsize(file_path)
            page_count = PDFInfo.get_page_count(file_path)

            return {
                'name': os.path.basename(file_path),
                'size': file_size,
                'pages': page_count,
                'exists': True,
                'size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception:
            return {
                'name': os.path.basename(file_path),
                'size': 0,
                'pages': 0,
                'exists': False
            }
