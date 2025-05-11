FROM python:3.13-slim

WORKDIR /spotyrate

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv

COPY . .

# Activate the virtual environment and install dependencies
RUN /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

EXPOSE 8000

CMD ["/venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
