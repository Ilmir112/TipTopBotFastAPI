FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

# КОММЕНТАРИЙ НИЖЕ ТОЛЬКО ДЛЯ DOCKER COMPOSE. РАСКОММЕНТИРУЙТЕ КОД, ЕСЛИ ВЫ ИСПОЛЬЗУЕТЕ ТОЛЬКО DOCKERFILE
# Предоставляет доступ контейнеру для запуска bash скрипта, если это необходимо
# Запускать bash скрипты без доступа к ним на ОС Linux невозможно. На Windows - возможно,
# но так как контейнеры работают на Linux, приходится давать доступ независимо от вашей ОС.
# RUN chmod a+x /zimaApp/docker/*.sh

# КОММЕНТАРИЙ НИЖЕ ТОЛЬКО ДЛЯ DOCKER COMPOSE. РАСКОММЕНТИРУЙТЕ КОД, ЕСЛИ ВЫ ИСПОЛЬЗУЕТЕ ТОЛЬКО DOCKERFILE
# Эта команда выведена в bash скрипт
# RUN alembic upgrade head

# КОММЕНТАРИЙ НИЖЕ ТОЛЬКО ДЛЯ DOCKER COMPOSE. РАСКОММЕНТИРУЙТЕ КОД, ЕСЛИ ВЫ ИСПОЛЬЗУЕТЕ ТОЛЬКО DOCKERFILE
# Эта команда также выведена в bash скрипт
 CMD ["gunicorn", "app.main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
# CMD ["gunicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
#gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:80