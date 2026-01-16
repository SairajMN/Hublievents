#!/bin/bash

# Hublievents Local Development Setup Script
# This script sets up the development environment for local testing

echo "🚀 Setting up Hublievents for local development..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.11+ and try again."
    exit 1
fi

# Check if Node.js is installed (for frontend development)
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Frontend will be served via Python's built-in server."
    echo "   For full development experience, install Node.js and npm."
fi

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Create uploads directory
mkdir -p uploads logs

# Setup database
echo "🗄️  Setting up database..."
python3 -c "
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

echo "✅ Backend setup complete!"
echo ""

# Return to root directory
cd ..

# Setup frontend (optional Node.js setup)
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    echo "🎨 Setting up frontend with Node.js..."
    cd frontend

    # Create package.json if it doesn't exist
    if [ ! -f "package.json" ]; then
        echo "📄 Creating package.json for frontend..."
        cat > package.json << 'EOF'
{
  "name": "hublievents-frontend",
  "version": "1.0.0",
  "description": "Hublievents luxury event customization platform frontend",
  "main": "index.html",
  "scripts": {
    "dev": "npx live-server --port=3000 --open=/",
    "serve": "npx live-server --port=3000",
    "build": "echo 'Frontend is static - no build needed'"
  },
  "devDependencies": {
    "live-server": "^1.2.2"
  },
  "keywords": ["wedding", "events", "customization", "luxury"],
  "author": "Hublievents",
  "license": "MIT"
}
EOF
    fi

    # Install dependencies
    npm install

    cd ..
    echo "✅ Frontend setup complete with Node.js!"
else
    echo "ℹ️  Frontend will be served via Python's built-in server"
fi

echo ""
echo "🎉 Setup complete! Run the following commands to start the development servers:"
echo ""
echo "1. Start the backend API:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo "2. Start the frontend (in a new terminal):"
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    echo "   cd frontend"
    echo "   npm run dev"
    echo "   # Frontend will be at: http://localhost:3000"
else
    echo "   cd frontend"
    echo "   python3 -m http.server 3000"
    echo "   # Frontend will be at: http://localhost:3000"
fi
echo ""
echo "3. Backend API will be at: http://localhost:8000"
echo "   - API docs: http://localhost:8000/api/docs"
echo "   - Admin dashboard: http://localhost:3000/admin/"
echo ""
echo "Default admin login:"
echo "   Email: admin@hublievents.com"
echo "   Password: admin123"
echo ""
echo "🚀 Happy coding!"
