## Project structure
```text
Directory structure:
└── nihosprop-stepik-mentor-metric/
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

