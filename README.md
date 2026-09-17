<div align="center">
    <h1>HealthTrack</h1>
    <p>Real-time hospital patient monitoring and vital signs telemetry platform.<br>Written in Python/Django</p>
</div>

## Features

- [X] Manage **patient admissions** and medical records with **last name search**
- [X] Generate **continuous vital signs** (Heart Rate, SpO₂, Temperature, Respiratory Rate, Blood Pressure) tailored to individual physiological profiles
- [X] Monitor incoming patient measurements with **live real-time updates**
- [X] Track vital sign trends through **real-time telemetry charts** and **historical measurement logs**
- [X] Brute force login protection with **rate limiting**

## Usage

First install `uv` and sync the project dependencies:

```bash
cd path/to/root/directory
pip install uv
uv sync
uv sync --group dev  # for devs only
```

Migrate database:

```bash
uv run manage.py migrate
```

Create a superuser for admin and creating accounts/doctors:

```bash
uv run manage.py createsuperuser
```

Start Redis server:

```bash
docker run -d --name redis -p 6379:6379 redis
```

Run the simulator:

```bash
uv run manage.py simulate
uv run manage.py simulate --interval 5  # secs between measurement rounds
```

Run ASGI/Daphne server:

```bash
uv run manage.py runserver
```

Access web application at `http://127.0.0.1:8000` or `http://localhost:8000`.
