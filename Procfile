web: python manage.py migrate && python init_accounts.py && python manage.py collectstatic --no-input && gunicorn --bind 0.0.0.0:$PORT projetAvocat.wsgi
