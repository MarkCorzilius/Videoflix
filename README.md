# Videoflix Backend

A Django REST API backend for a Netflix-style video streaming platform, providing user authentication and HLS-based adaptive video streaming.

## Tech Stack

- Python 3.14.0
- Django 6.0.6
- Django REST Framework 3.17.1
- djangorestframework-simplejwt — JWT authentication via HttpOnly cookies
- PostgreSQL (psycopg2-binary) — primary database
- Redis + django-rq — background job queue (video processing, emails)
- FFmpeg — video transcoding into HLS renditions (480p/720p/1080p)
- Gunicorn — production WSGI server
- Whitenoise — static file serving
- django-cors-headers — CORS handling
- django-debug-toolbar / django-import-export — development & admin tooling
- Docker & Docker Compose — containerized development environment

## Quick Instructions

Clone the repository.

```bash
git clone <repo>
```

Copy the environment template and fill in your own values (DB, Redis, superuser, secret key).

```bash
cp .env.template .env
```

Create a virtual environment (macOS/Linux).

```bash
python3 -m venv venv
```

Create a virtual environment (Windows).

```powershell
python -m venv venv
```

Activate the virtual environment (macOS/Linux).

```bash
source venv/bin/activate
```

Activate the virtual environment (Windows).

```powershell
venv\Scripts\activate
```

Install the project dependencies from `requirements.txt`.

```bash
pip install -r requirements.txt
```

After adding/updating a package, freeze the dependencies back into `requirements.txt`.

```bash
pip freeze > requirements.txt
```

Build and start all services (Django, PostgreSQL, Redis) with Docker Compose.

```bash
docker compose up --build
```

Follow the backend container logs.

```bash
docker compose logs -f web
```

Stop all running containers.

```bash
docker compose down
```

## API Endpoints

### Accounts (`/api/`)

| Endpoint                                       | Purpose                                                   |
| ---------------------------------------------- | --------------------------------------------------------- |
| `POST /api/register/`                          | Register a new user and send a verification email         |
| `GET /api/activate/<uidb64>/<token>/`          | Activate a user account via the emailed link              |
| `POST /api/login/`                             | Authenticate and receive access/refresh tokens as cookies |
| `POST /api/token/refresh/`                     | Refresh the access token using the refresh token cookie   |
| `POST /api/logout/`                            | Blacklist the refresh token and clear auth cookies        |
| `POST /api/password_reset/`                    | Request a password reset email                            |
| `POST /api/password_confirm/<uidb64>/<token>/` | Confirm and set a new password                            |

### Videos (`/api/`)

| Endpoint                                            | Purpose                                                     |
| --------------------------------------------------- | ----------------------------------------------------------- |
| `GET /api/video/`                                   | List all processed videos                                   |
| `GET /api/video/<movie_id>/<resolution>/index.m3u8` | Retrieve the HLS playlist for a video at a given resolution |
| `GET /api/video/<movie_id>/<resolution>/<segment>/` | Retrieve a single HLS video segment                         |

### Other

| Endpoint      | Purpose                                            |
| ------------- | -------------------------------------------------- |
| `/admin/`     | Django admin panel                                 |
| `/django-rq/` | Django RQ dashboard for monitoring background jobs |

## Testing

Tests are written with Django's test framework and located under each app's `tests/` folder (e.g. `accounts_app/tests/`).

Run the full test suite inside the running backend container:

```bash
docker compose exec web python manage.py test
```

Run tests for a single app:

```bash
docker compose exec web python manage.py test accounts_app
```
