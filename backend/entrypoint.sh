#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py shell <<'PY'
from django.contrib.auth import get_user_model

User = get_user_model()
username = "admin"
password = "admin"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email="", password=password)
PY

exec "$@"
