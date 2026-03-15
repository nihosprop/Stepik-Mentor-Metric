# Stepik Mentor Metric Bot

A Telegram bot for tracking mentor activity metrics on the Stepik platform. Automatically collects comments, calculates statistics, and generates reports for course mentors.

## Features

- **Mentor Management**: Add/remove mentors via Stepik profile links
- **Course Tracking**: Monitor multiple Stepik courses for new comments
- **Automatic Polling**: Fetches comments every 120 seconds with intelligent 
  caching
- **Statistics Aggregation**: Daily and monthly reports with efficiency metrics
- **Smart Cold Start**: Configurable historical data polling (2 days dev / 15 days prod)
- **Admin Reports**: Automated daily/monthly statistics sent to admins

## Technology Stack

| Component            | Technology                                        |
|----------------------|---------------------------------------------------|
| **Language**         | Python 3.14                                       |
| **Bot Framework**    | aiogram 3.x + aiogram-dialog                      |
| **DI Container**     | Dishka                                            |
| **Database**         | PostgreSQL 18 + SQLAlchemy 2.0 (Async)            |
| **Migrations**       | Alembic                                           |
| **Cache/FSM**        | Redis 8                                           |
| **Task Queue**       | Taskiq (Redis Stream Broker)                      |
| **Scheduler**        | Taskiq Scheduler (PostgreSQL source)              |
| **Config**           | Dynaconf + Pydantic                               |
| **Package Manager**  | uv                                                |
| **Containerization** | Docker + Docker Compose                           |
| **Code Quality**     | Ruff (linting/formatting)<br/> Ty (type checking) |

## Project Structure

```text
.
├── src/
│ ├── bot/             # Telegram bot handlers & dialogs
│ │ ├── dialogs/
│ │ │ ├── flows/
│ │ │ │ ├── courses/   # Course management dialog
│ │ │ │ ├── mentors/   # Mentor management dialog
│ │ │ │ ├── start/     # Main menu
│ │ │ │ └── statistic/ # Statistics reports
│ │ └── middlewares/   # ACL & other middlewares
│ ├── core/            # Application core (config, logging)
│ ├── db/
│ │ ├── models/        # SQLAlchemy models
│ │ └── repository/    # Data access layer
│ ├── infrastructure/
│ │ ├── di/providers/  # Dishka dependency providers
│ │ └── stepik/        # Stepik API client
│ ├── services/        # Business logic layer
│ ├── tasks/           # Background tasks (Taskiq)
│ ├── alembic/         # Database migrations
│ └── main.py          # Application entry point
├── tests/
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── Dockerfile
├── migrate.sh         # Migration automation script
├── pyproject.toml
├── settings.toml
└── .env.example
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Telegram Bot Token (from @BotFather)
- Stepik API Credentials (Client ID & Secret)
- Redis & PostgreSQL (included in Docker Compose)

### 1. Clone and Configure

```bash
git clone <repository-url>
cd stepik-mentor-metric-bot
cp .env.example .env
```
### 2. Edit ```.env```
```dotenv
APP_TAG=<actual-tag>
ENV_FOR_DYNACONF=production
BOT_TOKEN=your_telegram_bot_token

# Stepik
STEPIK_CLIENT_ID=your_stepik_client_id
STEPIK_CLIENT_SECRET=your_stepik_client_secret

# Redis
REDIS_PASSWORD=your_redis_password
REDIS_HOST=redis

# PostgreSQL
POSTGRES_USER=superuser
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=postgres_db
POSTGRES_DB=mentor_db
```
### 3. Run with Docker Compose
```bash
# Production
docker compose -f docker-compose.prod.yml up -d

# Development (with hot reload)
docker compose -f docker-compose.dev.yml up -d
```
### 4.  Check Logs
```bash
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f worker
docker compose -f docker-compose.prod.yml logs -f scheduler
```
## Development

### Local Setup with uv
```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --dev

# Run the bot
uv run python src/main.py
```

## Database Migrations
Use the automated migration script:
```bash
# Create and test a new migration
./migrate.sh "your_migration_description"
```
The script performs:
1. Starts the database container
2. Generates migration with `alembic revision --autogenerate`
3. Test Drive: Upgrade → Downgrade → Upgrade
4. Runs `alembic check` for model compliance
5. Stops the database

## Manual Alembic Commands
```bash
# Generate migration
docker compose -f docker-compose.dev.yml run --rm bot alembic revision --autogenerate -m "description"

# Apply migrations
docker compose -f docker-compose.dev.yml run --rm bot alembic upgrade head

# Check model compliance
docker compose -f docker-compose.dev.yml run --rm bot alembic check

# Rollback one version
docker compose -f docker-compose.dev.yml run --rm bot alembic downgrade -1
```

## Code Quality
```bash
# Format code
uv run ruff format src/

# Lint code
uv run ruff check src/

# Type checking (ty)
uv run ty src/
```
## API Integration
### Stepik OAuth2
1. The bot automatically:
2. Requests OAuth2 token from Stepik
3. Caches token in Redis (TTL: expires_in - 300 seconds)
4. Refreshes token on 401 Unauthorized
5. Handles rate limiting (429) with retry

## Cached Endpoints

* stepik_token — OAuth2 access token (Redis DB 1)
* courses_ids — Active course IDs (Redis DB 1, TTL: 1h)
* users_ids — Mentor IDs (Redis DB 1, TTL: 1h)
* time:course:{id} — Last poll timestamp per course

## Security
* Non-root user (appuser) in production container
* Secrets managed via environment variables
* PostgreSQL and Redis not exposed externally (internal network only)
* Passwords validated (min 7 characters) via Pydantic




















