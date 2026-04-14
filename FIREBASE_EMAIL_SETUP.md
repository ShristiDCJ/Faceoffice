# Firebase + Gmail SMTP Email Setup Guide

## What Was Implemented

✅ **Phase 1**: Visitor submits request → Stored in Firebase Realtime DB → Email sent to employee  
✅ **Phase 3**: Employee logs in → Fetches pending requests from Firebase → Views dashboard  
✅ **Phase 4**: Employee approves/rejects → Emails sent to BOTH visitor and employee  

## Files Created/Updated

### New Files:
- `app/services/email_service.py` - Gmail SMTP email sender
- `app/services/firebase_request_handler.py` - Firebase request logic with email triggers

### Updated Files:
- `app/routes/visitor.py` - Uses Firebase instead of SQLAlchemy
- `app/routes/employee.py` - Fetches from Firebase, handles approvals/rejections

## Environment Setup

### 1. Gmail Configuration

1. Go to https://myaccount.google.com/security
2. Enable **2-Factor Authentication** (if not already enabled)
3. Go to **App passwords** section
4. Select **Mail** and **Windows Computer**
5. Copy the 16-character password generated

### 2. Update `.env` File

```env
# Firebase
FIREBASE_DB_URL=https://facialauthenticator.firebaseio.com
FIREBASE_KEY_PATH=firebase-key.json

# Gmail SMTP (use app password from step 1)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password

# App Configuration
APP_URL=http://localhost:5000
FLASK_ENV=development
SECRET_KEY=your-secret-key
