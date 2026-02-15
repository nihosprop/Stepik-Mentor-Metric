## Project structure
```text
Stepik-Mentor-Metric/
    ├── alembic.ini
    ├── docker-compose.dev.yml
    ├── docker-compose.prod.yml
    ├── Dockerfile
    ├── migrate.sh
    ├── pyproject.toml
    ├── settings.toml
    ├── uv.lock
    ├── .env.example
    ├── src/
    │   ├── main.py
    │   ├── alembic/
    │   │   ├── README
    │   │   ├── env.py
    │   │   └── script.py.mako
    │   ├── bot/
    │   │   ├── dialogs/
    │   │   │   └── start/
    │   │   │       ├── dialog.py
    │   │   │       ├── getters.py
    │   │   │       ├── handlers.py
    │   │   │       └── states.py
    │   │   ├── factory/
    │   │   ├── middlewares/
    │   │   └── states/
    │   ├── common/
    │   │   └── telegram_utils.py
    │   ├── core/
    │   │   ├── logger.py
    │   │   └── main_config.py
    │   ├── db/
    │   │   ├── models/
    │   │   │   ├── base.py
    │   │   │   ├── mixins.py
    │   │   │   └── user.py
    │   │   └── repository/
    │   │       └── user_repo.py
    │   ├── infrastructure/
    │   │   ├── di/
    │   │   │   └── providers/
    │   │   │       ├── config.py
    │   │   │       ├── db.py
    │   │   │       ├── http.py
    │   │   │       ├── redis.py
    │   │   │       ├── repositories.py
    │   │   │       └── stepik.py
    │   │   └── stepik/
    │   │       └── client.py
    │   ├── services/
    │   └── tasks/
    ├── tests/
    └── .github/
        └── workflows/
            └── build-and-push.yml
```

**Stepik Mentor Metric Bot** — This is a Telegram bot designed for mentors on the Stepik platform. It allows you to track course metrics, manage user data and monitor new comments through integration with the Stepik API.

## 🚀 Technologies

The project is built on a modern Python technology stack:

*   **Python 3.14+**
*   **aiogram 3.x** — asynchronous framework for Telegram bots.
*   **aiogram-dialog** — library for creating complex interactive dialogs.
*   **Dishka** — modern DI container for dependency management.
*   **SQLAlchemy 2.0 & PostgreSQL** — working with a database through an asynchronous engine.
*   **Alembic** — managing database migrations.
*   **Redis** — used for FSM (Finite State Machine) bot and Stepik API data caching.
*   **Dynaconf & Pydantic** — flexible configuration management and settings validation.
*   **uv** — modern package manager and project builder.

## 🛠 Functionality

1.  **Integration with Stepik API:**Automatically receive OAuth2 tokens, cache them in Redis, and make API requests to retrieve user, course, and comment data.
2.  **Comment monitoring:** Receiving the latest course comments and generating direct links to them in the context of lessons.
3.  **User management:** Автоматическое сохранение и обновление данных Telegram-пользователей в базе данных (PostgreSQL) при взаимодействии с ботом.
4.  **Interactive dialogues:** Удобный интерфейс управления через систему окон и кнопок `aiogram-dialog`.
5.  **Logging:** Настраиваемая система логирования с поддержкой вывода в консоль и ротации файлов в режиме Production.

## 📦 Installation and launch

### Setting up the environment
Create a file `.env` based on example `.env.example` and fill in the required variables:
*   `BOT_TOKEN` — your bot's token from BotFather.
*   `STEPIK_CLIENT_ID` и `STEPIK_CLIENT_SECRET` — your application data Stepik.
*   Connection settings for PostgreSQL and Redis.

### Run via Docker (recommended)
