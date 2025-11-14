# Dependency Graph Visualizer

*Инструмент для визуализации графа зависимостей пакетов Maven, а также тестовых пакетов.*

## Текущий статус: завершен.

## Функциональность
- конфигурация через параметры командной строки;
- валидация входных параметров;
- вывод настроек в формате ключ-значение;
- получение прямых зависимостей из Maven-репозитория;
- вывод обратных зависимостей пакета;
- построение полного графа зависимостей с помощью BFS;
- обработка циклических зависимостей;
- поддержка тестовых репозиториев в txt-файлах;
- поддержка максимальной глубины анализа;
- визуализация графа зависимостей в формате svg.

## Использование
Убедитесь, что у вас установлены все необходимые модули:

```bash
pip install -r requirements.txt
```

Общий вид команды для запуска:

```bash
python src/cli.py --package <имя_пакета> --repo <url_репозитория> [опции]
```

**Допускается использование сокращений для параметров, они указаны в таблице «Доступные параметры»**

Продемонстрируем работу приложения на примере Maven-репозитория (https://repo.maven.apache.org/maven2).

Структура этого репозитория:
https://repo.maven.apache.org/maven2/GROUP_ID/ARTIFACT_ID/VERSION/

Рассмотрим на примере для **commons-lang3 версии 3.0**:
- GROUP_ID: `org.apache.commons`.
- ARTIFACT_ID: `commons-lang3`.
- VERSION: `3.0`.

Таким образом, запуск будет осуществлен со следующими параметрами:
```bash
python src/cli.py --package org.apache.commons:commons-lang3 --repo https://repo.maven.apache.org/maven2/ --version 3.0
```

## Доступные параметры
 Параметр | Описание |
|:----------:|:----------:|
| `--package / -p` `имя_пакета`    | `Имя анализируемого пакета (обязательный)`  |
| `--repo / -r` `ссылка_на_репозиторий`    | `URL репозитория или путь к файлу тестового репозитория (обязательный)`   |
| `--test-mode / -t`   | `Режим работы с тестовым репозиторием`   |
| `--version / -v` `номер_версии` | `Версия пакета` |
| `--graph / -g` | `Визуализация графа` |
| `--output / -o` `название_файла` | `Имя сгенерированного файла с изображением графа` |
| `--max-depth / -d` `количество_уровней` | `Максимальная глубина анализа зависимостей` |
| `--reverse / -R` `имя_пакета` | `Вывод графа обратных зависимостей` |

## Примеры запуска

### Базовый запуск
```bash
python src/cli.py -p com.example:my-package -r https://repo.maven.apache.org/maven2/
```

### С тестовым режимом
```bash
python src/cli.py -p TEST_PACKAGE -r tests/test_repo.txt -t
```
**Примечание: все тестовые репозитории находятся в директории tests; для корректной работы программы при использовании тестовых репозиториев необходим тестовый режим (`--test-mode / -t`).**

### С дополнительными параметрами
```bash
python src/cli.py -p com.example:lib -r /path/to/repo -v 1.0.0 -o graph.svg -d 3
```

## Тестирование

**Тест 1: получение зависимостей реального пакета**
```bash
python src/cli.py -p app.futured.donut:donut -r https://repo.maven.apache.org/maven2 -v 2.1.0 -R org.jetbrains.kotlin:kotlin-stdlib -o donut -g
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: app.futured.donut:donut
repo_url: https://repo.maven.apache.org/maven2
test_mode: False
version: 2.1.0
generate_graph: True
output_file: donut.svg
max_depth: unlimited
reverse_package: org.jetbrains.kotlin:kotlin-stdlib
------------------------------

Получение зависимостей для пакета app.futured.donut:donut...

Прямые зависимости пакета app.futured.donut:donut:
--------------------------------------------------
 1. org.jetbrains.kotlin:kotlin-stdlib-jdk7  1.3.72
 2. androidx.core:core-ktx                   1.1.0
--------------------------------------------------
Всего зависимостей: 2

Зависимости успешно получены.

Построение полного графа зависимостей...
Максимальная глубина: неограничена
Предупреждение: не удалось получить зависимости для androidx.core:core-ktx:1.1.0: POM-файл для androidx.core:core-ktx:1.1.0 не найден

Граф зависимостей сохранён в donut

Полный граф зависимостей для app.futured.donut:donut:2.1.0:
------------------------------------------------------------
app.futured.donut:donut:2.1.0
   org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.3.72
      org.jetbrains.kotlin:kotlin-stdlib:1.3.72
         org.jetbrains.kotlin:kotlin-stdlib-common:1.3.72
            org.jetbrains.kotlin:kotlin-test-common:1.3.72
               ↳ org.jetbrains.kotlin:kotlin-stdlib-common:1.3.72  (повтор)
               org.jetbrains.kotlin:kotlin-test-annotations-common:1.3.72
                  ↳ org.jetbrains.kotlin:kotlin-stdlib-common:1.3.72  (повтор)
                  ↳ org.jetbrains.kotlin:kotlin-test-common:1.3.72  (повтор)
            ↳ org.jetbrains.kotlin:kotlin-test-annotations-common:1.3.72  (повтор)
         org.jetbrains:annotations:13.0
         org.jetbrains.kotlin:kotlin-test-junit:1.3.72
            ↳ org.jetbrains.kotlin:kotlin-test-annotations-common:1.3.72  (повтор)
            org.jetbrains.kotlin:kotlin-test:1.3.72
               ↳ org.jetbrains.kotlin:kotlin-test-common:1.3.72  (повтор)
               ↳ org.jetbrains.kotlin:kotlin-stdlib:1.3.72  (повтор)
               ↳ org.jetbrains.kotlin:kotlin-test-junit:1.3.72  (повтор)
               junit:junit:4.12
                  org.hamcrest:hamcrest-core:1.3
            ↳ junit:junit:4.12  (повтор)
      ↳ org.jetbrains.kotlin:kotlin-test-junit:1.3.72  (повтор)
   androidx.core:core-ktx:1.1.0
------------------------------------------------------------
Всего узлов: 12

Обратные зависимости (кто зависит от org.jetbrains.kotlin:kotlin-stdlib:2.1.0):
------------------------------------------------------------
 1. app.futured.donut:donut:2.1.0
 2. org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.3.72
 3. org.jetbrains.kotlin:kotlin-test-junit:1.3.72
 4. org.jetbrains.kotlin:kotlin-test:1.3.72
------------------------------------------------------------
Всего обратных зависимостей: 4

Граф зависимостей успешно построен.
```
![Реальный граф](donut.svg)
**Примечание: наличие предупреждений не указывает на ошибку в работе программы. Не все зависимости находятся в Maven-репозитории.**

\
**Тест 2: обработка ошибок (нет переданного пакета)**
```bash
python src/cli.py --package "" --repo https://repo.maven.apache.org/maven2/
```

**Вывод**
```bash
Ошибка валидации конфигурации: Имя пакета обязательно для указания
```

\
**Тест 3: обработка ошибок (несуществующий пакет)**
```bash
python src/cli.py -p non.existent:package -r https://repo.maven.apache.org/maven2/ -v 1.0 -g
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: non.existent:package
repo_url: https://repo.maven.apache.org/maven2/
test_mode: False
version: 1.0
generate_graph: True
output_file: dependency_graph.svg
max_depth: unlimited
reverse_package: None
------------------------------

Получение зависимостей для пакета non.existent:package...
Критическая ошибка: POM-файл для non.existent:package:1.0 не найден
```

\
**Тест 4: тестовый репозиторий**
```bash
python src/cli.py -p A -r tests/test_repo.txt -t --reverse B -g -o test
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: A
repo_url: tests/test_repo.txt
test_mode: True
version: latest
generate_graph: True
output_file: test.svg
max_depth: unlimited
reverse_package: B
------------------------------

Получение зависимостей для пакета A...

Прямые зависимости пакета A:
--------------------------------------------------
 1. B:B                                      1.0.0
 2. C:C                                      1.0.0
--------------------------------------------------
Всего зависимостей: 2

Зависимости успешно получены.

Построение полного графа зависимостей...
Максимальная глубина: неограничена

Граф зависимостей сохранён в test

Полный граф зависимостей для A:latest:
------------------------------------------------------------
A:A:unknown
   B:B:1.0.0
      D:D:1.0.0
         H:H:1.0.0
            A:A:1.0.0
               ↳ B:B:1.0.0  (повтор)
               C:C:1.0.0
                  F:F:1.0.0
                     ↳ B:B:1.0.0  (повтор)
                     G:G:1.0.0
                  ↳ G:G:1.0.0  (повтор)
      E:E:1.0.0
   ↳ C:C:1.0.0  (повтор)
------------------------------------------------------------
Всего узлов: 9

Обратные зависимости (кто зависит от B):
------------------------------------------------------------
 1. A:A:1.0.0
 2. A:A:unknown
 3. C:C:1.0.0
 4. D:D:1.0.0
 5. F:F:1.0.0
 6. H:H:1.0.0
------------------------------------------------------------
Всего обратных зависимостей: 6

Граф зависимостей успешно построен.
```
![Тестовый граф](test.svg)


\
**Тест 5: огромный граф**
```bash
python src/cli.py -p gay.zharel.botlin:botlin -r https://repo.maven.apache.org/maven2/ -v 0.1.0 -d 1 -g -o huge_graph
```

**Вывод**
```bash
Текущая конфигурация:
------------------------------
package_name: gay.zharel.botlin:botlin
repo_url: https://repo.maven.apache.org/maven2/
test_mode: False
version: 0.1.0
generate_graph: True
output_file: huge_graph.svg
max_depth: 1
reverse_package: None
------------------------------

Получение зависимостей для пакета gay.zharel.botlin:botlin...

Прямые зависимости пакета gay.zharel.botlin:botlin:
--------------------------------------------------
 1. gay.zharel.botlin:units                  0.1.0
 2. org.jetbrains.kotlin:kotlin-stdlib       2.2.20
 3. edu.wpi.first.cscore:cscore-java         2025.3.2
 4. edu.wpi.first.cameraserver:cameraserver-java 2025.3.2
 5. edu.wpi.first.ntcore:ntcore-java         2025.3.2
 6. edu.wpi.first.wpilibj:wpilibj-java       2025.3.2
 7. edu.wpi.first.wpiutil:wpiutil-java       2025.3.2
 8. edu.wpi.first.wpimath:wpimath-java       2025.3.2
 9. edu.wpi.first.wpilibNewCommands:wpilibNewCommands-java 2025.3.2
10. edu.wpi.first.hal:hal-java               2025.3.2
11. org.ejml:ejml-simple                     0.43.1
12. com.fasterxml.jackson.core:jackson-annotations 2.15.2
13. com.fasterxml.jackson.core:jackson-core  2.15.2
14. com.fasterxml.jackson.core:jackson-databind 2.15.2
15. edu.wpi.first.thirdparty.frc2025.opencv:opencv-java 4.10.0-2
--------------------------------------------------
Всего зависимостей: 15

Зависимости успешно получены.

Построение полного графа зависимостей...
Максимальная глубина: 1

Граф зависимостей сохранён в huge_graph

Полный граф зависимостей для gay.zharel.botlin:botlin:0.1.0:
------------------------------------------------------------
gay.zharel.botlin:botlin:0.1.0
   gay.zharel.botlin:units:0.1.0
   org.jetbrains.kotlin:kotlin-stdlib:2.2.20
   edu.wpi.first.cscore:cscore-java:2025.3.2
   edu.wpi.first.cameraserver:cameraserver-java:2025.3.2
   edu.wpi.first.ntcore:ntcore-java:2025.3.2
   edu.wpi.first.wpilibj:wpilibj-java:2025.3.2
   edu.wpi.first.wpiutil:wpiutil-java:2025.3.2
   edu.wpi.first.wpimath:wpimath-java:2025.3.2
   edu.wpi.first.wpilibNewCommands:wpilibNewCommands-java:2025.3.2
   edu.wpi.first.hal:hal-java:2025.3.2
   org.ejml:ejml-simple:0.43.1
   com.fasterxml.jackson.core:jackson-annotations:2.15.2
   com.fasterxml.jackson.core:jackson-core:2.15.2
   com.fasterxml.jackson.core:jackson-databind:2.15.2
   edu.wpi.first.thirdparty.frc2025.opencv:opencv-java:4.10.0-2
------------------------------------------------------------
Всего узлов: 16

Граф зависимостей успешно построен.
```
![Огромный граф](huge_graph.svg)
