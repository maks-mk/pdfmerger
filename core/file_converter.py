"""
Модуль конвертации файлов в PDF
Поддерживает конвертацию различных форматов в PDF для объединения
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple

# Проверяем доступность библиотек для конвертации
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from docx2pdf import convert as docx_convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class FileConverter:
    """Класс для конвертации различных форматов файлов в PDF."""

    # Поддерживаемые форматы
    SUPPORTED_FORMATS = {
        'pdf': 'PDF файлы',
        'doc': 'Word документы (старый формат)',
        'docx': 'Word документы',
        'txt': 'Текстовые файлы',
        'jpg': 'JPEG изображения',
        'jpeg': 'JPEG изображения',
        'png': 'PNG изображения',
        'bmp': 'BMP изображения',
    }

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_files = []
        self._font_initialized = False

    @classmethod
    def get_file_filter(cls):
        """Возвращает фильтр файлов для QFileDialog."""
        extensions = []
        for ext in cls.SUPPORTED_FORMATS.keys():
            extensions.append(f"*.{ext}")

        all_supported = " ".join(extensions)

        filters = [
            f"Все поддерживаемые файлы ({all_supported})",
            "PDF файлы (*.pdf)",
            "Word документы (*.doc *.docx)",
            "Текстовые файлы (*.txt)",
            "Изображения (*.jpg *.jpeg *.png *.bmp)",
            "Все файлы (*.*)"
        ]

        return ";;".join(filters)

    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """Проверяет, поддерживается ли формат файла."""
        extension = Path(file_path).suffix.lower().lstrip('.')
        return extension in cls.SUPPORTED_FORMATS

    def convert_to_pdf(self, file_path: str) -> Tuple[bool, str]:
        """
        Конвертирует файл в PDF.

        Args:
            file_path: Путь к исходному файлу

        Returns:
            Tuple[bool, str]: (успех, путь_к_pdf_или_сообщение_об_ошибке)
        """
        if not os.path.exists(file_path):
            return False, f"Файл не найден: {file_path}"

        # Преобразуем в Path объект для удобной работы
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower().lstrip('.')

        # Если уже PDF, возвращаем как есть
        if extension == 'pdf':
            return True, file_path

        # Проверяем поддержку формата
        if not self.is_supported_format(file_path):
            return False, f"Неподдерживаемый формат: {extension}"

        try:
            # Создаем временный PDF файл
            temp_pdf = self._create_temp_pdf_path(file_path_obj.stem)

            # Конвертируем в зависимости от типа файла
            if extension in ['jpg', 'jpeg', 'png', 'bmp']:
                success, error = self._convert_image_to_pdf(file_path, temp_pdf)
            elif extension in ['doc', 'docx']:
                success, error = self._convert_word_to_pdf(file_path, temp_pdf)
            elif extension == 'txt':
                success, error = self._convert_text_to_pdf(file_path, temp_pdf)
            else:
                return False, f"Конвертация {extension} не реализована"

            if success:
                self.temp_files.append(temp_pdf)
                return True, temp_pdf
            else:
                return False, error

        except Exception as e:
            return False, f"Ошибка конвертации: {str(e)}"

    def _create_temp_pdf_path(self, base_name: str) -> str:
        """Создает путь для временного PDF файла."""
        temp_name = f"pdf_merger_temp_{base_name}_{len(self.temp_files)}.pdf"
        return os.path.join(self.temp_dir, temp_name)

    def _make_text_safe(self, text: str) -> str:
        """Делает текст безопасным для отрисовки, заменяя проблемные символы."""
        try:
            # Пытаемся закодировать в latin1 (базовая кодировка PDF)
            text.encode('latin1')
            return text
        except UnicodeEncodeError:
            # Заменяем символы, которые не могут быть отображены
            safe_text = ""
            for char in text:
                try:
                    char.encode('latin1')
                    safe_text += char
                except UnicodeEncodeError:
                    # Заменяем кириллические символы на транслитерацию
                    if char in self._cyrillic_map:
                        safe_text += self._cyrillic_map[char]
                    else:
                        safe_text += '?'  # Неизвестный символ
            return safe_text

    @property
    def _cyrillic_map(self):
        """Карта транслитерации кириллических символов."""
        return {
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }

    def _setup_cyrillic_font(self):
        """Настраивает шрифт с поддержкой кирилицы."""
        if not REPORTLAB_AVAILABLE:
            print("⚠️ reportlab не доступен, используется базовый шрифт")
            return "Helvetica"

        if self._font_initialized:
            # Возвращаем уже инициализированный шрифт
            try:
                # Проверяем, зарегистрирован ли наш шрифт
                from reportlab.pdfbase.pdfmetrics import getFont
                getFont('CyrillicFont')
                return 'CyrillicFont'
            except:
                return "Helvetica"

        try:
            # Пытаемся найти системные шрифты с поддержкой кирилицы
            import platform
            system = platform.system()

            font_paths = []
            if system == "Windows":
                # Windows шрифты
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf",
                    "C:/Windows/Fonts/tahoma.ttf",
                    "C:/Windows/Fonts/verdana.ttf"
                ]
            elif system == "Darwin":  # macOS
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/Library/Fonts/Arial.ttf"
                ]
            else:  # Linux
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/TTF/arial.ttf",
                    "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
                ]

            # Ищем первый доступный шрифт
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # Регистрируем шрифт
                        pdfmetrics.registerFont(TTFont('CyrillicFont', font_path))
                        self._font_initialized = True
                        print(f"✅ Найден шрифт с поддержкой кирилицы: {os.path.basename(font_path)}")
                        return 'CyrillicFont'
                    except Exception as e:
                        print(f"⚠️ Не удалось загрузить шрифт {font_path}: {e}")
                        continue

            # Если не нашли системные шрифты
            print("⚠️ Системные шрифты с кириллицей не найдены, используется Helvetica")
            print("   Кирилица может отображаться некорректно")
            self._font_initialized = True
            return "Helvetica"

        except Exception as e:
            print(f"⚠️ Ошибка при настройке шрифта: {e}")
            self._font_initialized = True
            return "Helvetica"

    def _convert_image_to_pdf(self, image_path: str, output_path: str) -> Tuple[bool, str]:
        """Конвертирует изображение в PDF."""
        if not PIL_AVAILABLE or not REPORTLAB_AVAILABLE:
            return False, "Для конвертации изображений нужны библиотеки: pip install Pillow reportlab"

        try:
            # Открываем изображение
            with Image.open(image_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Получаем размеры
                img_width, img_height = img.size

                # Создаем PDF
                c = canvas.Canvas(output_path, pagesize=A4)
                page_width, page_height = A4

                # Вычисляем масштаб для вписывания в страницу
                scale_x = (page_width - 40) / img_width  # 20px отступ с каждой стороны
                scale_y = (page_height - 40) / img_height
                scale = min(scale_x, scale_y, 1.0)  # Не увеличиваем, только уменьшаем

                # Вычисляем позицию для центрирования
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                x = (page_width - scaled_width) / 2
                y = (page_height - scaled_height) / 2

                # Добавляем изображение
                c.drawImage(ImageReader(img), x, y, scaled_width, scaled_height)
                c.save()

            return True, ""

        except Exception as e:
            return False, f"Ошибка конвертации изображения: {str(e)}"

    def _convert_word_to_pdf(self, word_path: str, output_path: str) -> Tuple[bool, str]:
        """Конвертирует Word документ в PDF."""
        if not DOCX2PDF_AVAILABLE:
            return False, "Для конвертации Word документов нужна библиотека: pip install docx2pdf"

        try:
            # Конвертируем Word в PDF
            docx_convert(word_path, output_path)

            # Проверяем, что файл создан
            if os.path.exists(output_path):
                return True, ""
            else:
                return False, "Не удалось создать PDF файл"

        except Exception as e:
            return False, f"Ошибка конвертации Word документа: {str(e)}"

    def _convert_text_to_pdf(self, text_path: str, output_path: str) -> Tuple[bool, str]:
        """Конвертирует текстовый файл в PDF."""
        if not REPORTLAB_AVAILABLE:
            return False, "Для конвертации текста нужна библиотека: pip install reportlab"

        try:
            # Читаем текстовый файл
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # Создаем PDF
            c = canvas.Canvas(output_path, pagesize=A4)
            page_width, page_height = A4

            # Настройки текста
            font_size = 12
            line_height = 14
            margin = 40
            max_width = page_width - 2 * margin

            # Настраиваем шрифт с поддержкой кирилицы
            font_name = self._setup_cyrillic_font()

            # Разбиваем текст на строки
            lines = text_content.split('\n')
            y_position = page_height - margin

            c.setFont(font_name, font_size)

            for line in lines:
                # Проверяем, помещается ли строка на страницу
                if y_position < margin + line_height:
                    c.showPage()  # Новая страница
                    y_position = page_height - margin
                    c.setFont(font_name, font_size)

                # Разбиваем длинные строки
                if c.stringWidth(line) > max_width:
                    words = line.split(' ')
                    current_line = ""

                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        if c.stringWidth(test_line) <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                try:
                                    c.drawString(margin, y_position, current_line)
                                except Exception:
                                    # Если не удается отрисовать, заменяем проблемные символы
                                    safe_line = self._make_text_safe(current_line)
                                    c.drawString(margin, y_position, safe_line)
                                y_position -= line_height
                                if y_position < margin + line_height:
                                    c.showPage()
                                    y_position = page_height - margin
                                    c.setFont(font_name, font_size)
                            current_line = word

                    if current_line:
                        try:
                            c.drawString(margin, y_position, current_line)
                        except Exception:
                            safe_line = self._make_text_safe(current_line)
                            c.drawString(margin, y_position, safe_line)
                        y_position -= line_height
                else:
                    try:
                        c.drawString(margin, y_position, line)
                    except Exception:
                        safe_line = self._make_text_safe(line)
                        c.drawString(margin, y_position, safe_line)
                    y_position -= line_height

            c.save()
            return True, ""

        except UnicodeDecodeError:
            # Пробуем другие кодировки
            try:
                with open(text_path, 'r', encoding='cp1251') as f:
                    text_content = f.read()
                # Повторяем процесс с новой кодировкой
                return self._convert_text_to_pdf_content(text_content, output_path)
            except Exception:
                return False, "Не удалось прочитать текстовый файл (проблема с кодировкой)"
        except Exception as e:
            return False, f"Ошибка конвертации текста: {str(e)}"

    def _convert_text_to_pdf_content(self, content: str, output_path: str) -> Tuple[bool, str]:
        """Вспомогательный метод для конвертации текстового содержимого в PDF."""
        try:
            c = canvas.Canvas(output_path, pagesize=A4)
            page_width, page_height = A4

            font_size = 12
            line_height = 14
            margin = 40
            max_width = page_width - 2 * margin

            # Настраиваем шрифт с поддержкой кирилицы
            font_name = self._setup_cyrillic_font()

            lines = content.split('\n')
            y_position = page_height - margin

            c.setFont(font_name, font_size)

            for line in lines:
                if y_position < margin + line_height:
                    c.showPage()
                    y_position = page_height - margin
                    c.setFont(font_name, font_size)

                if c.stringWidth(line) > max_width:
                    words = line.split(' ')
                    current_line = ""

                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        if c.stringWidth(test_line) <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                try:
                                    c.drawString(margin, y_position, current_line)
                                except Exception:
                                    safe_line = self._make_text_safe(current_line)
                                    c.drawString(margin, y_position, safe_line)
                                y_position -= line_height
                                if y_position < margin + line_height:
                                    c.showPage()
                                    y_position = page_height - margin
                                    c.setFont(font_name, font_size)
                            current_line = word

                    if current_line:
                        try:
                            c.drawString(margin, y_position, current_line)
                        except Exception:
                            safe_line = self._make_text_safe(current_line)
                            c.drawString(margin, y_position, safe_line)
                        y_position -= line_height
                else:
                    try:
                        c.drawString(margin, y_position, line)
                    except Exception:
                        safe_line = self._make_text_safe(line)
                        c.drawString(margin, y_position, safe_line)
                    y_position -= line_height

            c.save()
            return True, ""

        except Exception as e:
            return False, f"Ошибка создания PDF: {str(e)}"

    def cleanup_temp_files(self):
        """Удаляет все временные файлы."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Не удалось удалить временный файл {temp_file}: {e}")

        self.temp_files.clear()

    def get_missing_dependencies(self) -> list:
        """Возвращает список отсутствующих зависимостей."""
        missing = []

        if not PIL_AVAILABLE:
            missing.append("Pillow (для изображений)")

        if not REPORTLAB_AVAILABLE:
            missing.append("reportlab (для текста и изображений)")

        if not DOCX2PDF_AVAILABLE:
            missing.append("docx2pdf (для Word документов)")

        return missing
