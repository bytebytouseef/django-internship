# Intern Management System

A full-stack web application for managing intern profiles and assignments.

## Backend Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   ```
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

Backend will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Build Tailwind CSS** (optional, for development)
   ```bash
   npm run build:css
   ```

The frontend is served by Django at `http://localhost:8000`

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/schema/swagger/
- **ReDoc**: http://localhost:8000/api/schema/redoc/

## Key Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/refresh/` - Refresh access token

### Intern Profile
- `GET /api/interns/` - List all interns
- `GET /api/interns/me/` - Get current user's profile
- `PUT /api/interns/me_update/` - Update current user's profile

### Assignments
- `GET /api/assignments/` - List assignments
- `POST /api/assignments/{id}/submit/` - Submit assignment work
- `GET /api/assignments/submissions/` - List submissions

### Admin
- `POST /api/assignments/submissions/{id}/approve/` - Approve submission
- `POST /api/assignments/submissions/{id}/reject/` - Reject submission

## Features

- ✅ User registration and authentication with JWT
- ✅ Intern profile management
- ✅ Assignment creation and submission
- ✅ Admin dashboard with filtering and search
- ✅ Pagination and sorting
- ✅ REST API with Swagger documentation
- ✅ Tailwind CSS styling
- ✅ Vanilla JavaScript with async/await
- ✅ HttpOnly cookie refresh token storage

## Project Structure

```
├── backend/
│   ├── config/          # Django settings and URLs
│   ├── apps/
│   │   ├── users/       # User authentication
│   │   ├── interns/     # Intern profiles
│   │   └── assignments/ # Assignments and submissions
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css    # Tailwind CSS
│   ├── js/
│   │   ├── main.js      # Router
│   │   ├── auth.js      # Auth logic
│   │   ├── api.js       # API client
│   │   └── components/  # UI components
│   ├── tailwind.config.js
│   └── package.json
└── .gitignore
```

## Testing

### Create Test Data

1. Login to admin panel: `http://localhost:8000/admin/`
2. Create test interns and assignments
3. Test user flows through the main interface

### Test as Admin

In admin panel, mark a user with `is_admin=True` to access admin dashboard.

## Default Login

After creating a superuser, use those credentials to login to the application.

## Environment Variables (Optional)

Create a `.env` file in the backend directory:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:8000
```

## Troubleshooting

**CORS errors**: Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
**401 errors**: Token might be expired, try refreshing the page
**Migration errors**: Run `python manage.py makemigrations` then `python manage.py migrate`

## Future Enhancements

- File upload for submissions
- Email notifications
- Real-time notifications with WebSockets
- Advanced reporting and analytics
- Mobile app
- User role hierarchy

## License

MIT
