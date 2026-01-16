# Hublievents Backend API

Production-grade backend for the Luxury Event & Shamiyana Customization Platform.

## 🚀 Features

- **Secure Authentication**: JWT-based authentication with refresh tokens
- **Role-Based Access Control**: Guest, Customer, Admin, and Super Admin roles
- **Design Management**: Save, version, and share design customizations
- **Enquiry System**: Customer inquiries with status tracking
- **Gallery Management**: Secure image upload and management
- **Audit Logging**: Comprehensive admin action logging
- **Security First**: CSRF protection, rate limiting, security headers
- **Scalable Architecture**: PostgreSQL support, Redis-ready caching

## 🛠️ Tech Stack

- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic schemas
- **Security**: OWASP-compliant security headers, CSRF protection
- **Rate Limiting**: SlowAPI integration

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Environment configuration
├── database.py            # Database setup and session management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (copy from .env.example)
├── logs/                  # Application logs
├── uploads/               # File uploads directory
├── migrations/            # Database migrations
├── models/                # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py           # User model with RBAC
│   ├── design.py         # Design customization model
│   ├── enquiry.py        # Customer enquiry model
│   ├── gallery.py        # Image gallery model
│   └── admin_log.py      # Audit logging model
├── schemas/               # Pydantic request/response schemas
│   ├── __init__.py
│   ├── user.py           # User-related schemas
│   ├── design.py         # Design-related schemas
│   ├── enquiry.py        # Enquiry-related schemas
│   ├── gallery.py        # Gallery-related schemas
│   └── admin.py          # Admin-related schemas
├── auth/                  # Authentication and authorization
│   ├── __init__.py
│   ├── jwt.py            # JWT token management
│   ├── password.py       # Password hashing utilities
│   └── dependencies.py   # Auth dependencies
├── routes/                # API route handlers
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── users.py          # User management routes
│   ├── designs.py        # Design routes
│   ├── enquiries.py      # Enquiry routes
│   ├── gallery.py        # Gallery routes
│   └── admin.py          # Admin routes
├── security/              # Security middleware
│   ├── __init__.py
│   └── middleware.py     # Security headers, CSRF protection
└── utils/                 # Utility functions
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login`
3. **Refresh Token**: `POST /api/v1/auth/refresh`

Include the access token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

## 🗄️ Database

### Development (SQLite)
- Default database: `hublievents.db`
- Automatic table creation on startup

### Production (PostgreSQL)
Set environment variables in `.env`:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Access + refresh token rotation
- **CSRF Protection**: Double-submit cookie pattern
- **Rate Limiting**: Configurable request limits
- **Security Headers**: OWASP recommended headers
- **Input Validation**: Comprehensive Pydantic validation
- **Audit Logging**: All admin actions logged

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/password-reset/request` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset
- `POST /api/v1/auth/password/change` - Change password

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile

### Designs
- `POST /api/v1/designs` - Create new design
- `GET /api/v1/designs` - List user designs
- `GET /api/v1/designs/{id}` - Get design details
- `PUT /api/v1/designs/{id}` - Update design
- `DELETE /api/v1/designs/{id}` - Delete design
- `POST /api/v1/designs/{id}/share` - Share design
- `POST /api/v1/designs/{id}/clone` - Clone design

### Enquiries
- `POST /api/v1/enquiries` - Submit enquiry
- `GET /api/v1/enquiries` - List user enquiries
- `GET /api/v1/enquiries/{id}` - Get enquiry details

### Gallery (Admin)
- `POST /api/v1/gallery/upload` - Upload image
- `GET /api/v1/gallery/images` - List gallery images
- `PUT /api/v1/gallery/images/{id}` - Update image metadata
- `DELETE /api/v1/gallery/images/{id}` - Delete image

### Admin
- `GET /api/v1/admin/stats` - Dashboard statistics
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/enquiries` - List all enquiries
- `PUT /api/v1/admin/enquiries/{id}` - Update enquiry status
- `GET /api/v1/admin/logs` - Audit logs

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_auth.py
```

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `DEBUG` | Debug mode | `false` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./hublievents.db` |
| `JWT_SECRET_KEY` | JWT signing key | Auto-generated |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |
| `UPLOAD_PATH` | File upload directory | `uploads` |
| `MAX_UPLOAD_SIZE` | Max upload size (bytes) | `10485760` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: support@hublievents.com
- Documentation: [API Docs](http://localhost:8000/api/docs)

---

**Built with ❤️ for luxury event experiences**
