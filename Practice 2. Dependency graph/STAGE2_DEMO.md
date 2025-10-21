# Демонстрация Этапа 2: Сбор данных

## Тестовые примеры

### 1. Тестовый репозиторий - Пакет A (с зависимостями)
```bash
python dependency_visualizer.py -p A -v 1.0 -r test_repo.txt --test-mode
```

**Результат:**
- B
- C
- Всего: 2 зависимости

### 2. Тестовый репозиторий - Пакет D (без зависимостей)
```bash
python dependency_visualizer.py -p D -v 1.0 -r test_repo.txt --test-mode
```

**Результат:**
- Зависимости отсутствуют

### 3. Maven репозиторий - JUnit 4.13.2
```bash
python dependency_visualizer.py -p junit:junit -v 4.13.2 -r https://repo.maven.apache.org/maven2
```

**Результат:**
- org.hamcrest:hamcrest-core
- Всего: 1 зависимость

### 4. Maven репозиторий - Google Guava 31.0-jre
```bash
python dependency_visualizer.py -p com.google.guava:guava -v 31.0-jre -r https://repo.maven.apache.org/maven2
```

**Результат:**
- com.google.guava:failureaccess
- com.google.guava:listenablefuture
- com.google.code.findbugs:jsr305
- org.checkerframework:checker-qual
- com.google.errorprone:error_prone_annotations
- com.google.j2objc:j2objc-annotations
- Всего: 6 зависимостей

### 5. Maven репозиторий - Apache Commons Lang 3.12.0
```bash
python dependency_visualizer.py -p org.apache.commons:commons-lang3 -v 3.12.0 -r https://repo.maven.apache.org/maven2
```

**Результат:**
- org.junit:junit-bom
- Всего: 1 зависимость

## Реализованная функциональность

✅ Парсинг Maven POM файлов (XML)
✅ HTTP запросы для получения POM файлов из репозитория
✅ Парсинг тестового репозитория из текстового файла
✅ Фильтрация test и optional зависимостей
✅ Вывод прямых зависимостей на экран
✅ Обработка ошибок сети и парсинга
✅ Использование только стандартных библиотек Python

## Что НЕ используется

❌ Готовые библиотеки для работы с Maven
❌ Сторонние HTTP клиенты
❌ Внешние парсеры XML
❌ Менеджеры пакетов для получения зависимостей

## Технический стек

- `urllib.request` - HTTP запросы
- `xml.etree.ElementTree` - парсинг XML
- Стандартная библиотека Python

