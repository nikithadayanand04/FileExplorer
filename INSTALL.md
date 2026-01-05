# Installation Guide

## Quick Fix for Current Setup

You've already created the virtual environment. To fix the missing dependencies:

```bash
cd backend
source venv/bin/activate
pip install fastapi uvicorn pydantic-settings aiofiles python-multipart cryptography opencv-python-headless pillow numpy
```

Then start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Fresh Installation

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Starting the Application

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Troubleshooting

### ModuleNotFoundError: No module named 'pydantic_settings'
**Solution**: Install pydantic-settings
```bash
pip install pydantic-settings
```

### ModuleNotFoundError: No module named 'cv2'
**Solution**: Install opencv-python-headless
```bash
pip install opencv-python-headless
```

### MediaPipe Warning
This is normal - MediaPipe is optional. Face detection will use OpenCV only.

### Port Already in Use
Change the port:
```bash
uvicorn app.main:app --reload --port 8001
```

## Verification

Test that everything works:
1. Backend: Visit http://localhost:8000/docs (should show API docs)
2. Frontend: Visit http://localhost:3000 (should show file explorer)
3. Upload a test file and verify classification works

