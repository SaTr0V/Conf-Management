# Unix Shell Emulator

*Эмулятор командной строки Unix-подобных систем с графическим интерфейсом.*

## Функциональность

- **GUI** на **tkinter** c историей и прокруткой;
- Отладочные сообщения (**debug**);
- Конфигурация через аргументы при запуске;
- Виртуальная файловая система и взаимодействие с ней.

## Файловая система

Файловая система находится целиком в памяти.

Готовый шаблон файловой системы можно загрузить из xml-файлов, хранящихся директории `vfs_structures`.

Для двоичных данных используется формат **base64**.

## Команды

- `ls` - список файлов и директорий;
- `cd` - смена текущей директории;
- `conf-dump` - вывод конфигурации эмулятора;
- `echo` - вывод текста;
- `tac` - вывод содержимого файла в обратном порядке строк;
- `find` - поиск файлов и директорий по имени;
- `wc` - подсчет строк, слов и символов в файле;
- `exit` - завершение работы эмулятора.

## Запуск

### Поддерживаемые параметры запуска:

- `--debug`;
- `--script emulator_scripts/«имя_скрипта.vsh»`;
- `--vfs vfs_structures/«имя_файловой_системы.xml»`.

### Примеры запусков

**Базовый запуск**

```bash
python main.py
```

**Запуск с отладочными сообщениями**
```bash
python main.py --debug
```

**Запуск со скриптом (например, стартовый скрипт)**
```bash
python main.py --script emulator_scripts/startup.vsh
```

**Запуск с готовой файловой системой**
```bash
python main.py --vfs vfs_structures/complex.xml
```

**Комбинированный запуск**
```bash
python main.py --debug --script emulator_scripts/startup_stage_3.vsh --vfs vfs_structures/binary.xml
```

## Демонстрация работы программы

```bash
# Приветственное сообщение
Добро пожаловать в эмулятор командной строки VFS!
Доступные команды: ls, cd, exit, conf-dump, echo, tac, find, wc, mkdir, touch
Для выхода введите 'exit'

Введенные параметры запуска: --debug --vfs vfs_structures/complex.xml --script emulator_scripts/for_readme.vsh
Выполнение скрипта: /Users/mac/Documents/2 курс/3 семестр/Конфигурационное управление/Conf-Management/Practice 1: Unix-shell-emulator/emulator_scripts/for_readme.vsh
------------------------------

VFS:/$ echo "1. Навигация и базовые команды"
"1. Навигация и базовые команды"

VFS:/$ cd /home/user/documents
Переход в /home/user/documents

VFS:/home/user/documents$ ls
multi_line.txt
project1.txt
project2.txt


VFS:/home/user/documents$ echo "2. Поиск и анализ файлов"
"2. Поиск и анализ файлов"

VFS:/home/user/documents$ find . -name *.txt
./project1.txt
./project2.txt
./multi_line.txt

VFS:/home/user/documents$ wc project1.txt
  5  11  71 project1.txt


VFS:/home/user/documents$ echo "3. Обработка содержимого"
"3. Обработка содержимого"

VFS:/home/user/documents$ tac project1.txt
Завершение проекта 1
Третья строка
Вторая строка
Первая строка
Проект 1


VFS:/home/user/documents$ echo "4. Работа с переменными окружения"
"4. Работа с переменными окружения"

VFS:/home/user/documents$ echo "Текущий пользователь: $USER, домашняя директория: $HOME"
"Текущий пользователь: mac, домашняя директория: /Users/mac"


VFS:/home/user/documents$ echo "5. Создание директорий и файлов"
"5. Создание директорий и файлов"

VFS:/home/user/documents$ cd /
Переход в /

VFS:/$ mkdir new_project
Директория создана

VFS:/$ cd new_project
Переход в /new_project

VFS:/new_project$ touch README.md
Файл создан

VFS:/new_project$ mkdir src
Директория создана

VFS:/new_project$ cd src
Переход в /new_project/src

VFS:/new_project/src$ touch main.py
Файл создан

VFS:/new_project/src$ cd /new_project
Переход в /new_project

VFS:/new_project$ mkdir docs
Директория создана

VFS:/new_project$ mkdir tests
Директория создана


VFS:/new_project$ echo "6. Проверка созданной структуры"
"6. Проверка созданной структуры"

VFS:/new_project$ ls
README.md
docs
src
tests

VFS:/new_project$ find . -name *
./README.md
./src
./src/main.py
./docs
./tests


VFS:/new_project$ echo "7. Обработка ошибок создания"
"7. Обработка ошибок создания"

VFS:/new_project$ mkdir src
Директория уже существует

VFS:/new_project$ touch docs
touch: docs: директория с таким именем уже существует

VFS:/new_project$ mkdir /invalid/path
mkdir: Родительская директория не найдена

VFS:/new_project$ conf-dump
КОНФИГУРАЦИЯ ЭМУЛЯТОРА
vfs_path: /Users/mac/Documents/2 курс/3 семестр/Конфигурационное управление/Conf-Management/Practice 1: Unix-shell-emulator/vfs_structures/complex.xml
script_path: /Users/mac/Documents/2 курс/3 семестр/Конфигурационное управление/Conf-Management/Practice 1: Unix-shell-emulator/emulator_scripts/for_readme.vsh
debug: True
current_directory: /Users/mac/Documents/2 курс/3 семестр/Конфигурационное управление/Conf-Management/Practice 1: Unix-shell-emulator/src
```