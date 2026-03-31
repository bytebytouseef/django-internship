# Frontend Setup Guide

The frontend is served by Django and doesn't require a separate development server.

## Files Overview

- `index.html` - Main SPA entry point
- `css/style.css` - Tailwind CSS configuration
- `js/main.js` - Router and app initialization
- `js/auth.js` - Authentication and token management
- `js/api.js` - Central API client with auto-refresh
- `js/components/` - UI components (login, dashboard, profile, assignments, admin)

## Development

The frontend is served as static files by Django. To use Tailwind CSS compilation:

```bash
npm install
npm run build:css
```

## How It Works

1. **Single Page Application**: Routes handled by `main.js` with hash-based navigation
2. **Token Storage**: Access tokens in localStorage, refresh tokens in HttpOnly cookies
3. **Auto-refresh**: API client automatically refreshes tokens on 401
4. **Vanilla JS**: No framework dependencies, pure async/await with Fetch API

## Components

- **login.js** - Login and registration forms
- **dashboard.js** - Main navigation and layout
- **profile.js** - View and edit intern profile
- **assignments.js** - List and submit assignments
- **admin.js** - Admin dashboard for managing interns and submissions
