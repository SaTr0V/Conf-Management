# Визуализатор графа зависимостей Maven

Инструмент для визуализации графа зависимостей пакетов Maven.

## Описание

Этот проект представляет собой CLI-приложение для анализа и визуализации зависимостей Maven пакетов. Инструмент позволяет строить граф зависимостей с учетом транзитивности и выводить его в формате SVG.

## Этап 1: Минимальный прототип с конфигурацией ✓

Реализован базовый CLI-интерфейс с настраиваемыми параметрами и валидацией входных данных.

### Возможности

- Парсинг параметров командной строки.
- Валидация всех входных параметров.
- Обработка ошибок для некорректных данных.
- Вывод конфигурации в формате ключ-значение.

### Параметры командной строки

| Параметр | Короткая форма | Описание | Обязательный |
|----------|----------------|----------|--------------|
| `--package` | `-p` | Имя анализируемого пакета | Да |
| `--repository` | `-r` | URL репозитория или путь к файлу | Да |
| `--test-mode` | - | Режим работы с тестовым репозиторием | Нет |
| `--version` | `-v` | Версия пакета | Да |
| `--output` | `-o` | Имя файла для графа (по умолчанию: dependency_graph.svg) | Нет |
| `--max-depth` | `-d` | Максимальная глубина анализа (по умолчанию: 3) | Нет |

### Установка и запуск

```bash
# Запуск с минимальными параметрами
python dependency_visualizer.py -p org.springframework:spring-core -v 5.3.0 -r https://repo.maven.apache.org/maven2

# Запуск с полными параметрами
python dependency_visualizer.py -p org.springframework:spring-core -v 5.3.0 -r https://repo.maven.apache.org/maven2 -o output.svg -d 5
```

### Примеры использования

#### Успешный запуск с реальным репозиторием
```bash
python dependency_visualizer.py -p org.springframework:spring-core -v 5.3.0 -r https://repo.maven.apache.org/maven2
```

#### Успешный запуск с тестовым репозиторием
```bash
python dependency_visualizer.py -p A -v 1.0 -r test_repo.txt --test-mode
```

### Обработка ошибок

Программа валидирует все параметры и выводит понятные сообщения об ошибках:

1. **Пустое имя пакета**
   ```bash
   python dependency_visualizer.py -p "" -v 1.0 -r https://repo.maven.apache.org/maven2
   # Ошибка: имя пакета не может быть пустым
   ```

2. **Некорректный URL репозитория**
   ```bash
   python dependency_visualizer.py -p A -v 1.0 -r invalid-url
   # Ошибка: URL репозитория должен начинаться с http:// или https://
   ```

3. **Несуществующий файл в тестовом режиме**
   ```bash
   python dependency_visualizer.py -p A -v 1.0 -r nonexistent.txt --test-mode
   # Ошибка: файл тестового репозитория не найден
   ```

4. **Пустая версия**
   ```bash
   python dependency_visualizer.py -p A -v "" -r https://repo.maven.apache.org/maven2
   # Ошибка: версия пакета не может быть пустой
   ```

5. **Некорректное расширение файла вывода**
   ```bash
   python dependency_visualizer.py -p A -v 1.0 -r https://repo.maven.apache.org/maven2 -o output.png
   # Ошибка: выходной файл должен иметь расширение .svg
   ```

6. **Некорректная глубина**
   ```bash
   python dependency_visualizer.py -p A -v 1.0 -r https://repo.maven.apache.org/maven2 -d 0
   # Ошибка: максимальная глубина должна быть не меньше 1
   ```

### Требования

- Python 3.6 или выше
- Стандартная библиотека Python (внешние зависимости не требуются)

---

## Этап 2: Сбор данных ✓

Реализован сбор информации о зависимостях из Maven репозитория и тестового репозитория.

### Возможности

- Получение информации о зависимостях из реального Maven репозитория через HTTP
- Парсинг Maven POM файлов (XML) для извлечения зависимостей
- Работа с тестовым репозиторием (текстовый формат)
- Вывод прямых зависимостей для заданного пакета
- Фильтрация test и optional зависимостей

### Формат тестового репозитория

Тестовый репозиторий представляет собой текстовый файл в формате:
```
# Комментарий
PACKAGE:VERSION -> DEPENDENCY1, DEPENDENCY2, ...
```

Пример (`test_repo.txt`):
```
A:1.0 -> B, C
B:1.0 -> D
C:1.0 -> D, E
D:1.0 ->
E:1.0 -> F
F:1.0 ->
```

### Примеры использования

#### Тестовый репозиторий
```bash
# Пакет A с двумя зависимостями
python dependency_visualizer.py -p A -v 1.0 -r test_repo.txt --test-mode

# Пакет B с одной зависимостью
python dependency_visualizer.py -p B -v 1.0 -r test_repo.txt --test-mode

# Пакет D без зависимостей
python dependency_visualizer.py -p D -v 1.0 -r test_repo.txt --test-mode
```

#### Реальный Maven репозиторий
```bash
# JUnit 4.13.2 (одна зависимость)
python dependency_visualizer.py -p junit:junit -v 4.13.2 -r https://repo.maven.apache.org/maven2

# Google Guava (пакет с множеством зависимостей)
python dependency_visualizer.py -p com.google.guava:guava -v 31.0-jre -r https://repo.maven.apache.org/maven2

# Apache Commons Lang (без зависимостей)
python dependency_visualizer.py -p org.apache.commons:commons-lang3 -v 3.12.0 -r https://repo.maven.apache.org/maven2
```

### Вывод программы

Программа выводит:
1. Конфигурацию параметров
2. Список всех прямых зависимостей
3. Общее количество зависимостей

Пример вывода для JUnit:
```
============================================================
Прямые зависимости для junit:junit:4.13.2
============================================================
1. org.hamcrest:hamcrest-core

Всего зависимостей: 1
```

Пример вывода для Google Guava:
```
============================================================
Прямые зависимости для com.google.guava:guava:31.0-jre
============================================================
1. com.google.guava:failureaccess
2. com.google.guava:listenablefuture
3. com.google.code.findbugs:jsr305
4. org.checkerframework:checker-qual
5. com.google.errorprone:error_prone_annotations
6. com.google.j2objc:j2objc-annotations

Всего зависимостей: 6
```

### Технические детали

- **Без использования готовых библиотек**: Используются только стандартные библиотеки Python
- **HTTP запросы**: `urllib.request` для загрузки POM файлов
- **XML парсинг**: `xml.etree.ElementTree` для разбора Maven POM файлов
- **Поддержка Maven namespace**: Корректная обработка XML с namespace `http://maven.apache.org/POM/4.0.0`
- **Обработка ошибок**: Понятные сообщения при проблемах с сетью или некорректных данных
- **Фильтрация зависимостей**: Исключаются зависимости со scope=test и optional=true

---

## Лицензия

Учебный проект