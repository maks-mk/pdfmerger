"""
Рабочий поток для объединения PDF файлов
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2 не установлен")
    PdfReader = PdfWriter = None


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
            
            if not PdfWriter or not PdfReader:
                self.error.emit("PyPDF2 не установлен")
                return
            
            # Создаем объект для записи
            pdf_writer = PdfWriter()
            
            # Проходим по всем файлам
            for file_path in self.file_paths:
                if not os.path.exists(file_path):
                    self.error.emit(f"Файл не найден: {file_path}")
                    return
                
                try:
                    # Читаем PDF файл
                    pdf_reader = PdfReader(file_path)
                    
                    # Добавляем все страницы в writer
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                        
                except Exception as e:
                    self.error.emit(f"Ошибка при чтении файла {os.path.basename(file_path)}: {str(e)}")
                    return
            
            # Проверяем, что есть страницы для записи
            if len(pdf_writer.pages) == 0:
                self.error.emit("Нет страниц для объединения")
                return
            
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            
            # Записываем объединенный PDF
            with open(self.output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Проверяем, что файл создан
            if os.path.exists(self.output_path):
                self.finished.emit(self.output_path)
            else:
                self.error.emit("Не удалось создать выходной файл")
                
        except Exception as e:
            self.error.emit(f"Неожиданная ошибка: {str(e)}")


class PDFValidator:
    """Класс для валидации PDF файлов."""
    
    @staticmethod
    def is_valid_pdf(file_path):
        """Проверяет, является ли файл валидным PDF."""
        if not os.path.exists(file_path):
            return False, "Файл не существует"
        
        if not file_path.lower().endswith('.pdf'):
            return False, "Файл не является PDF"
        
        try:
            if PdfReader:
                reader = PdfReader(file_path)
                # Проверяем, что есть хотя бы одна страница
                if len(reader.pages) == 0:
                    return False, "PDF файл пустой"
                return True, "OK"
            else:
                return False, "PyPDF2 не установлен"
        except Exception as e:
            return False, f"Ошибка чтения PDF: {str(e)}"
    
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
        try:
            if PdfReader and os.path.exists(file_path):
                reader = PdfReader(file_path)
                return len(reader.pages)
            return 0
        except Exception:
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
