@echo off
start python manage.py runserver
timeout /t 5 /nobreak
start http://localhost:8000

