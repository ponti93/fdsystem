# 🚀 Fraud Detection System - Deployment Guide

## 📂 Repository: https://github.com/ponti93/fdsystem.git

## 🎯 Deployment Architecture

**Single Docker Container** serving both:
- 🐍 **FastAPI Backend** (`/api/*` endpoints)
- ⚛️ **React Frontend** (static files served from `/`)

## 🔧 Local Development Setup

### Prerequisites:
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git

### Quick Start:
```bash
git clone https://github.com/ponti93/fdsystem.git
cd fdsystem
python setup_system.py
```

### Manual Setup:
```bash
# Backend
cd backend
pip install -r requirements.txt
python setup_database.py
python main.py

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

## 🐳 Docker Development

```bash
# Build and run with Docker
docker build -t fraud-detection-system .
docker run -p 8000:8000 fraud-detection-system

# Access application
http://localhost:8000
```

## 🌐 Render Deployment

### Step 1: Connect GitHub to Render
1. Login to [Render](https://render.com)
2. Connect your GitHub account
3. Select `ponti93/fdsystem` repository

### Step 2: Configure Service
- **Environment**: Docker
- **Build Command**: Auto-detected from Dockerfile
- **Start Command**: Auto-detected from Dockerfile
- **Plan**: Free

### Step 3: Environment Variables
```
DATABASE_HOST=<render-postgres-host>
DATABASE_PORT=5432
DATABASE_NAME=fraud_detection_db
DATABASE_USER=postgres
DATABASE_PASSWORD=<render-postgres-password>
FLUTTERWAVE_PUBLIC_KEY=<your-flutterwave-public-key>
FLUTTERWAVE_SECRET_KEY=<your-flutterwave-secret-key>
FLUTTERWAVE_ENCRYPTION_KEY=<your-flutterwave-encryption-key>
```

### Step 4: Database Migration
1. **Create Render PostgreSQL** database
2. **Update environment variables** with new database credentials
3. **Run database setup** (automatic on first deployment)

## 🔗 Access URLs

### Local Development:
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Production (Render):
- **Application**: https://fraud-detection-system.onrender.com
- **API Docs**: https://fraud-detection-system.onrender.com/docs
- **Health Check**: https://fraud-detection-system.onrender.com/health

## 🛡️ Default Credentials

**Admin Access**: `admin_token123`
**Analyst Access**: `analyst_token123`

## 📊 Features Included

✅ Real-time fraud detection with RNN model  
✅ Flutterwave payment integration  
✅ Transaction monitoring dashboard  
✅ Risk analytics and reporting  
✅ User management interface  
✅ ML model training and management  
✅ System configuration panel  

## 🔧 Troubleshooting

### Common Issues:
1. **Port conflicts**: Change port in uvicorn.run()
2. **Database connection**: Check PostgreSQL credentials
3. **Model training**: Ensure sufficient memory (2GB+)
4. **Frontend build**: Check Node.js version compatibility

### Support:
- Check `/health` endpoint for system status
- Review application logs for detailed error information
- Ensure all environment variables are properly set
