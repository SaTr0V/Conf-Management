# Комплексное тестирование этапа 5

echo "ТЕСТИРОВАНИЕ ЭТАПА 5"

echo "1. НАЧАЛЬНОЕ СОСТОЯНИЕ"
ls

echo "2. СОЗДАНИЕ ТЕКСТОВОЙ СТРУКТУРЫ"
mkdir test_workspace
cd test_workspace
mkdir dir1
touch file1.txt
ls

echo "3. СОЗДАНИЕ ВЛОЖЕННОЙ СТРУКТУРЫ"
mkdir dir1/subdir1
mkdir dir1/subdir2
mkdir dir1/subdir2/deep
touch dir1/subdir1/config.conf
touch dir1/subdir2/data.csv
touch dir1/subdir2/deep/secret.key
ls dir1/subdir1/
ls dir1/subdir2/
ls dir1/subdir2/deep/

echo "4. ОБРАБОТКА ОШИБОК"
echo "Попытка создать в несуществующей директории:"
mkdir /invalid/path/here
touch /another/invalid/file.txt

echo "5. СОЗДАНИЕ СЛОЖНОГО ПРОЕКТА"
cd /
mkdir /projects
mkdir /projects/web_app
mkdir /projects/web_app/backend
mkdir /projects/web_app/frontend
mkdir /projects/web_app/docs
touch /projects/web_app/readme.md
touch /projects/web_app/backend/server.py
touch /projects/web_app/backend/config.json
touch /projects/web_app/frontend/index.html
touch /projects/web_app/frontend/style.css
touch /projects/web_app/docs/api.md

echo "6. ПРОВЕРКА ПРОЕКТА"
cd /projects/web_app
ls
find . -name *.py
find . -name *.md
find . -name *.json

echo "7. ФИНАЛЬНАЯ КОНФИГУРАЦИЯ"
conf-dump

echo "Скрипт завершен"