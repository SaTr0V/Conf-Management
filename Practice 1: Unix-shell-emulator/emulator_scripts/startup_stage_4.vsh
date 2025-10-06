# Комплексное тестирование этапа 4

echo "1. НАВИГАЦИЯ"
cd /
ls
cd /home/user/documents
ls

echo "2. ТЕСТИРОВАНИЕ КОМАНДЫ wc"
echo "Статистика для различных файлов:"
wc project1.txt
wc project2.txt
wc /etc/hosts
echo "Обработка ошибок wc:"
wc nonexistent_file
wc /home

echo "3. ТЕСТИРОВАНИЕ КОМАНДЫ tac"
echo "Обратный вывод файлов:"
tac project1.txt
tac project2.txt
echo "Обработка ошибок tac:"
tac no_file
tac /etc

echo "4. ТЕСТИРОВАНИЕ КОМАНДЫ find"
echo "Поиск по различным шаблонам:"
find /home -name *.txt
find / -name hosts
find /etc -name *conf*
find /home -name project*
echo "Поиск всех файлов:"
find /home -name *

echo "5. КОМБИНАЦИИ КОМАНД"
echo "Найдем все .txt файлы и выведем их в обратном порядке:"
find /home -name *.txt
tac project1.txt
tac project2.txt
echo "Статистика по всем найденным файлам:"
wc project1.txt
wc project2.txt

echo "6. КОНФИГУРАЦИЯ СИСТЕМЫ"
conf-dump

echo "Скрипт завершен"