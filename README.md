# 1. Подготовка базы данных PostgreSQL
## Создание базы данных и пользователя

Войдите в PostgreSQL

```bash
sudo -u postgres psql
```

В консоли PostgreSQL выполните:
```bash
CREATE DATABASE your_database_name;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
```

# 2. Настройка переменных окружения

Укажите свои данные базы в файле .env в корне проекта:

```
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

# 3. Настройка виртуального окружения

## Создание виртуального окружения
```bash
python3 -m venv venv
```

## Активация виртуального окружения
На Linux/Mac:
```
source venv/bin/activate
```
На Windows:
```
# venv\Scripts\activate
```
# 4. Установка зависимостей

Установка всех зависимостей из requirements.txt
```bash
pip install -r requirements.txt
```

# 5. Запуск приложения
Запуск main.py
```bash
python src/main.py
```
или
```bash
python3 src/main.py
```