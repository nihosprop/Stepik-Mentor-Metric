## Project structure
```text
Stepik-Mentor-Metric/
├── src/
│   ├── bot/
│   │   ├── dialogs/
│   │   │   ├── start/
│   │   │   │   ├── dialog.py
│   │   │   │   ├── getters.py
│   │   │   │   ├── handlers.py
│   │   │   │   └── states.py
│   │   ├── factory/
│   │   ├── middlewares/
│   │   ├── states/
│   │   └── providers.py
│   ├── common/
│   ├── core/
│   │   ├── logger.py
│   │   └── main_config.py
│   ├── db/
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   └── user.py
│   │   ├── repository/
│   ├── services/
│   ├── tasks/
│   └── main.py
├── tests/
├── Dockerfile
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── settings.toml
├── temp.py
└── uv.lock
