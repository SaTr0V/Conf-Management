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