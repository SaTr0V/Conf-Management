# Unix Shell Emulator

Эмулятор командной строки Unix-подобных систем с графическим интерфейсом.

## Функциональность

- GUI на tkinter;
- Поддержка базовых команд (ls, cd, exit).
- Команда conf-dump
- Поддержка скриптов
- Отладочные сообщения (debug)

## Запуск

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

**Комбинированный запуск**
```bash
python main.py --debug --script emulator_scripts/startup.vsh
```