@echo off
REM Hublievents Local Development Setup Script (Windows)
REM This script sets up the development environment for local testing

echo 🚀 Setting up Hublievents for local development...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed. Please install Python 3.11+ and try again.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed (optional)
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Node.js not found. Frontend will be served via Python's built-in server.
    echo For full development experience, install Node.js from: https://nodejs.org/
    set NODE_INSTALLED=0
) else (
    set NODE_INSTALLED=1
)

REM Setup backend
echo 📦 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🐍 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Create uploads directory
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

REM Setup database
echo 🗄️  Setting up database...
python -c "
from database import create_tables
from models import User
from auth.password import get_password_hash
from database import get_db
from sqlalchemy.orm import Session

# Create tables
create_tables()

# Create default admin user
db = next(get_db())
try:
    admin = User(
        name='System Admin',
        email='admin@hublievents.com',
        hashed_password=get_password_hash('admin123'),
        role='super_admin',
        is_active=True,
        is_banned=False
    )
    db.add(admin)
    db.commit()
    print('✅ Admin user created: admin@hublievents.com / admin123')
except Exception as e:
    print(f'ℹ️  Admin user may already exist: {e}')
    db.rollback()
finally:
    db.close()
"

echo ✅ Backend setup complete!
echo.

REM Return to root directory
cd ..

REM Setup frontend (optional Node.js setup)
if %NODE_INSTALLED%==1 (
    echo 🎨 Setting up frontend with Node.js...
    cd frontend

    REM Create package.json if it doesn't exist
    if not exist "package.json" (
        echo 📄 Creating package.json for frontend...
        echo { > package.json
        echo   "name": "hublievents-frontend", >> package.json
        echo   "version": "1.0.0", >> package.json
        echo   "description": "Hublievents luxury event customization platform frontend", >> package.json
        echo   "main": "index.html", >> package.json
        echo   "scripts": { >> package.json
        echo     "dev": "npx live-server --port=3000 --open=/", >> package.json
        echo     "serve": "npx live-server --port=3000", >> package.json
        echo     "build": "echo 'Frontend is static - no build needed'" >> package.json
        echo   }, >> package.json
        echo   "devDependencies": { >> package.json
        echo     "live-server": "^1.2.2" >> package.json
        echo   }, >> package.json
        echo   "keywords": ["wedding", "events", "customization", "luxury"], >> package.json
        echo   "author": "Hublievents", >> package.json
        echo   "license": "MIT" >> package.json
        echo } >> package.json
    )

    REM Install dependencies
    npm install

    cd ..
    echo ✅ Frontend setup complete with Node.js!
) else (
    echo ℹ️  Frontend will be served via Python's built-in server
)

echo.
echo 🎉 Setup complete! Run the following commands to start the development servers:
echo.
echo 1. Start the backend API (in one terminal):
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 2. Start the frontend (in another terminal):
if %NODE_INSTALLED%==1 (
    echo    cd frontend
    echo    npm run dev
    echo    REM Frontend will be at: http://localhost:3000
) else (
    echo    cd frontend
    echo    python -m http.server 3000
    echo    REM Frontend will be at: http://localhost:3000
)
echo.
echo 3. Backend API will be at: http://localhost:8000
echo    - API docs: http://localhost:8000/api/docs
echo    - Admin dashboard: http://localhost:3000/admin/
echo.
echo Default admin login:
echo    Email: admin@hublievents.com
echo    Password: admin123
echo.
echo 🚀 Happy coding!

pause
