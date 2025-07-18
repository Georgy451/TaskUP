README# TaskUP

TaskUP — это платформа для управления задачами и проведения игровых сессий с поддержкой пользователей, комнат и профилей.

## Быстрый старт

### 1. Клонирование репозитория
```sh
git clone https://github.com/Georgy451/TaskUP.git
cd TaskUP/trackup
```

---

## Frontend (React + Vite)

1. Перейдите в папку frontend:
   ```sh
   cd frontend
   ```
2. Установите зависимости:
   ```sh
   npm install
   ```
3. Запустите приложение:
   ```sh
   npm run dev
   ```

---

## Room Service (FastAPI)

1. Перейдите в папку room-service:
   ```sh
   cd ../room-service
   ```
2. Создайте и активируйте виртуальное окружение:
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
4. Запустите сервер:
   ```sh
   uvicorn main:app --reload
   ```

---

## User Service (FastAPI)

1. Перейдите в папку user-service:
   ```sh
   cd ../user-service
   ```
2. Создайте и активируйте виртуальное окружение:
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
4. Запустите сервер:
   ```sh
   uvicorn main:app --reload
   ```

---

## Зависимости

### Frontend
- react
- react-dom
- react-router-dom
- vite
- typescript
- eslint
- @vitejs/plugin-react
- @types/react
- @types/react-dom
- другие dev-зависимости (см. package.json)

### Room Service
- fastapi
- redis>=4.2.0
- uvicorn
- pydantic

### User Service
- fastapi
- uvicorn[standard]
- SQLAlchemy
- asyncpg
- alembic
- passlib[bcrypt]
- python-jose
- pydantic
- python-dotenv

---