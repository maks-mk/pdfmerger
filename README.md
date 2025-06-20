# PDF Merger Pro v2.2

Универсальное приложение для создания PDF документов из любых источников с полной поддержкой кирилицы и автоматической конвертацией файлов.

## ✨ Особенности

### 🚀 **Новое в версии 2.2**
- 🔄 **Конвертация файлов** - автоматическое преобразование Word, изображений, текста в PDF
- 🔤 **Полная поддержка кирилицы** - корректное отображение русского текста во всех PDF
- 📁 **Универсальный Drag & Drop** - поддержка всех форматов файлов
- ⚡ **Оптимизированное объединение** - использование PyMuPDF для лучшего качества
- 🛡️ **Автоматическая очистка** - управление временными файлами

### 🎯 **Основные функции**
- 🎨 **Современный интерфейс** - адаптирован под низкие разрешения (1366x768+)
- 👁️ **Предварительный просмотр** - просмотр PDF перед объединением
- 🖼️ **Мультипредпросмотр** - одновременный просмотр нескольких файлов
- 🔄 **Изменение порядка** - перестановка файлов в списке
- ⚡ **Фоновая обработка** - объединение не блокирует интерфейс
- 🛡️ **Валидация файлов** - проверка корректности на всех этапах
- 📊 **Информативный статус** - отображение прогресса и подробных сообщений

## 🚀 Быстрый старт

### Установка зависимостей

```bash
# Обязательные зависимости
pip install PyPDF2 qtawesome PyQt6

# Рекомендуемые зависимости (для полной функциональности)
pip install PyMuPDF Pillow reportlab

# Дополнительные зависимости
pip install docx2pdf  # Для конвертации Word документов
```

### Быстрая установка всех зависимостей
```bash
pip install -r requirements.txt
```

## 📁 Поддерживаемые форматы

### ✅ **Основные форматы** (работают всегда)
- **📄 PDF** - прямое добавление без конвертации
- **📝 TXT** - текстовые файлы с автоматическим форматированием и поддержкой кирилицы
- **🖼️ JPG/JPEG, PNG, BMP** - изображения с оптимальным масштабированием

### 🔄 **Дополнительные форматы** (требуют библиотек)
- **📄 DOC/DOCX** - документы Microsoft Word (требует `docx2pdf`)

### 🔤 **Поддержка кирилицы**
- ✅ **Автоматический поиск** системных шрифтов с поддержкой русского языка
- ✅ **Корректное отображение** кириллических символов в PDF
- ✅ **Оптимизация объединения** с использованием PyMuPDF для лучшей работы с кириллицей
- ✅ **Кроссплатформенность** - работает на Windows, macOS, Linux

### 📊 **Качество конвертации**
- **Изображения**: автоматическое масштабирование под A4, сохранение пропорций
- **Текст**: красивое форматирование, автоматический перенос строк
- **Word**: сохранение оригинального форматирования, поддержка изображений и таблиц

📖 **Подробная документация**: [FILE_CONVERSION.md](FILE_CONVERSION.md) | [CYRILLIC_FIX.md](CYRILLIC_FIX.md)

### Запуск приложения

```bash
python main.py
```

Или старый способ:
```bash
python pdf_merger_app.py
```

## 📁 Структура проекта

```
pdf_merger_app/
├── main.py                 # Новый главный файл запуска
├── pdf_merger_app.py       # Старый монолитный файл (для совместимости)
├── core/                   # Основная логика
│   ├── __init__.py
│   └── pdf_worker.py       # Рабочие потоки и валидация
├── ui/                     # Пользовательский интерфейс
│   ├── __init__.py
│   ├── main_window.py      # Главное окно
│   ├── widgets.py          # Пользовательские виджеты
│   ├── styles.py           # Стили CSS
│   └── preview_dialogs.py  # Диалоги предпросмотра
└── README.md
```

## 🎯 Использование

### 📁 **Добавление файлов любых форматов**
1. **Перетаскивание**: Перетащите файлы любых поддерживаемых форматов в область списка
2. **Кнопка**: Нажмите "Добавить файлы" и выберите PDF, Word, изображения или текстовые файлы
3. **Автоматическая конвертация**: Файлы автоматически преобразуются в PDF

### 🔄 **Управление списком**
- **Изменение порядка**: Используйте стрелки ↑↓ или перетаскивание
- **Удаление**: Выберите файл и нажмите "Удалить выбранный"
- **Очистка**: Нажмите "Очистить все" для удаления всех файлов
- **Статус конвертации**: Видите прогресс преобразования файлов

### 👁️ **Предварительный просмотр**
- **Один файл**: Выберите файл и нажмите "Просмотр" (работает с кириллицей)
- **Все файлы**: Нажмите "Предпросмотр всех файлов" - мультипредпросмотр с навигацией
- **Проверка качества**: Убедитесь, что кирилица отображается корректно

### 🚀 **Объединение**
1. Добавьте минимум 2 файла (любых поддерживаемых форматов)
2. Нажмите "🚀 Объединить PDF файлы"
3. Выберите место сохранения
4. Дождитесь завершения процесса
5. Получите единый PDF с корректной кириллицей

### 💡 **Примеры рабочих процессов**

#### 📋 Создание отчета:
```
1. Добавить титульную страницу (Word документ)
2. Добавить графики и диаграммы (изображения PNG/JPG)
3. Добавить текстовые заметки (TXT файлы с кириллицей)
4. Добавить приложения (существующие PDF)
5. Объединить → получить полный отчет в одном PDF
```

#### 📚 Объединение документации:
```
1. Добавить README (текстовый файл)
2. Добавить скриншоты интерфейса (изображения)
3. Добавить техническую документацию (Word файлы)
4. Объединить → получить единую документацию
```

## 🔧 Технические детали

### Архитектура
- **Модульная структура** - разделение на логические компоненты
- **MVC паттерн** - разделение данных, представления и логики
- **Асинхронная обработка** - использование QThread для фоновых задач
- **Валидация данных** - проверка файлов перед обработкой

### Основные классы

#### Core модули
- `PDFMergerWorker` - рабочий поток для объединения PDF
- `PDFValidator` - валидация PDF файлов
- `PDFInfo` - получение информации о PDF

#### UI модули
- `PDFMergerMainWindow` - главное окно приложения
- `PDFListWidget` - список файлов с drag & drop
- `StatusWidget` - виджет статуса с цветовой индикацией
- `PDFPreviewDialog` - диалог предварительного просмотра

### Зависимости

#### **Обязательные**
- **PyQt6** - графический интерфейс
- **PyPDF2** - базовая работа с PDF файлами
- **qtawesome** - иконки FontAwesome

#### **Рекомендуемые** (для полной функциональности)
- **PyMuPDF** - предварительный просмотр + оптимальное объединение
- **Pillow** - конвертация изображений в PDF
- **reportlab** - создание PDF из текста с поддержкой кирилицы

#### **Дополнительные**
- **docx2pdf** - конвертация Word документов

## 🎨 Дизайн

### Цветовая схема
- **Основной**: #667eea (синий градиент)
- **Успех**: #28a745 (зеленый)
- **Предупреждение**: #ffc107 (желтый)
- **Ошибка**: #dc3545 (красный)
- **Информация**: #17a2b8 (голубой)

### Адаптивность
- **Минимальное разрешение**: 1366x768
- **Компактные элементы** для маленьких экранов
- **Масштабируемые окна** с ограничениями

## 🐛 Устранение неполадок

### Ошибки импорта
```bash
# Переустановите зависимости
pip uninstall PyPDF2 qtawesome PyQt6
pip install PyPDF2 qtawesome PyQt6
```

### Проблемы с предпросмотром
```bash
# Установите PyMuPDF
pip install PyMuPDF
```

### Ошибки на Windows
```bash
# Используйте виртуальное окружение
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 📝 История версий

### v2.2 (Текущая) - "Universal PDF Creator"
- 🚀 **Конвертация файлов** - поддержка Word, изображений, текста
- 🔤 **Полная поддержка кирилицы** - корректное отображение русского текста в PDF
- 📁 **Универсальный Drag & Drop** - поддержка всех форматов файлов
- ⚡ **Оптимизированное объединение** - приоритетное использование PyMuPDF
- 🛡️ **Автоматическая очистка** - управление временными файлами
- 🔧 **Улучшенная диагностика** - подробные сообщения об ошибках
- 🎯 **Graceful degradation** - работа при отсутствии дополнительных библиотек
- 📊 **Качественная конвертация** - сохранение форматирования и пропорций

### v2.1
- ✅ Мультипредпросмотр файлов
- ✅ Горячие клавиши для навигации
- ✅ Статистика файлов в предпросмотре
- ✅ Улучшенная информация о файлах
- ✅ Адаптивный интерфейс предпросмотра

### v2.0
- ✅ Полный рефакторинг кода
- ✅ Модульная архитектура
- ✅ Улучшенный UI/UX
- ✅ Адаптация под низкие разрешения
- ✅ Валидация файлов
- ✅ Улучшенная обработка ошибок

### v1.0
- ✅ Базовое объединение PDF
- ✅ Простой интерфейс
- ✅ Drag & Drop поддержка

## 🔨 Сборка исполняемого файла

### Подготовка к сборке
```bash
# Установите PyInstaller
pip install PyInstaller

# Проверьте готовность к сборке (новое в v2.2)
python build.py --check-only
```

### Сборка приложения
```bash
# Полная сборка v2.2 (рекомендуется)
python build.py

# Проверка зависимостей перед сборкой
python build.py --check-only

# Ручная сборка (если нужно)
pyinstaller --onefile --windowed --name=PDFMergerPro --icon=pdf.ico main.py
```

### Результат сборки v2.2
- **Исполняемый файл**: `dist/PDFMergerPro.exe`
- **Размер**: ~80-150 МБ (больше из-за дополнительных библиотек)
- **Требования**: Windows 10+, не требует Python
- **Включено**: все библиотеки для конвертации и кирилицы
- **Функциональность**: полная поддержка всех форматов

Подробные инструкции: [BUILD.md](BUILD.md)

## 💡 Рекомендации по использованию

### 🔤 **Для работы с кириллицей**
```bash
# Установите PyMuPDF для оптимального качества
pip install PyMuPDF

# Убедитесь, что в системе есть шрифты с поддержкой кирилицы:
# Windows: Arial, Calibri, Tahoma (обычно есть)
# macOS: Arial, Helvetica (обычно есть)
# Linux: sudo apt install fonts-dejavu fonts-liberation
```

### 📄 **Для конвертации документов**
```bash
# Для изображений и текста
pip install Pillow reportlab

# Для Word документов (только Windows)
pip install docx2pdf
```

### ⚡ **Для максимальной производительности**
```bash
# Установите все рекомендуемые зависимости
pip install PyMuPDF Pillow reportlab docx2pdf

# Используйте SSD для временных файлов
# Закройте другие приложения при обработке больших файлов
```

### 🎯 **Лучшие практики**
- **Проверяйте предпросмотр** перед объединением, особенно для файлов с кириллицей
- **Используйте качественные исходники** - изображения в высоком разрешении
- **Группируйте файлы по типам** - сначала текст, потом изображения
- **Сохраняйте резервные копии** важных документов перед обработкой

## 🤝 Вклад в проект

Приветствуются любые улучшения! Создавайте Issues и Pull Requests.

## 📄 Лицензия

MIT License - используйте свободно для любых целей.
