# Backend Setup Guide

Navigate to backend directory and run:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API available at: http://localhost:8000/api
Admin: http://localhost:8000/admin
Swagger: http://localhost:8000/api/schema/swagger/
