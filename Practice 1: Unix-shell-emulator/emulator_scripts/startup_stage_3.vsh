# Комплексное тестирование всех функций третьего этапа

echo "1. ТЕСТ НАЧАЛЬНОГО СОСТОЯНИЯ"
conf-dump
ls

echo "2. НАВИГАЦИЯ ПО КОРНЕВОЙ ДИРЕКТОРИИ"
ls /
cd /etc
ls
cd /var
ls
cd /home
ls

echo "3. МНОГОУРОВНЕВАЯ НАВИГАЦИЯ"
cd user/documents
ls
cd ../..
ls
cd /home/user/downloads
ls

echo "4. ОБРАБОТКА ОШИБОК"
cd /nonexistent_directory
ls /invalid_path
cd /home/user/nonexistent_file

echo "5. ОТНОСИТЕЛЬНЫЕ ПУТИ И СПЕЦИАЛЬНЫЕ СИМВОЛЫ"
cd .
ls
cd ..
ls
cd .././user/./documents
ls

echo "6. ФИНАЛЬНОЕ СОСТОЯНИЕ"
conf-dump

echo "Скрипт завершен"