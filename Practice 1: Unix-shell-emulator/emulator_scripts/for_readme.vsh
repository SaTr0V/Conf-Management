echo "1. Навигация и базовые команды"
cd /home/user/documents
ls

echo "2. Поиск и анализ файлов"
find . -name *.txt
wc project1.txt

echo "3. Обработка содержимого"
tac project1.txt

echo "4. Работа с переменными окружения"
echo "Текущий пользователь: $USER, домашняя директория: $HOME"

echo "5. Создание директорий и файлов"
cd /
mkdir new_project
cd new_project
touch README.md
mkdir src
cd src
touch main.py
cd /new_project
mkdir docs
mkdir tests

echo "6. Проверка созданной структуры"
ls
find . -name *

echo "7. Обработка ошибок создания"
mkdir src
touch docs
mkdir /invalid/path

conf-dump