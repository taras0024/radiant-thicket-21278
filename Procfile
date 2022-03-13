release: python manage.py migrate
web: gunicorn planeks.wsgi --log-file -
worker: celery -A planeks worker -l info -P gevent
