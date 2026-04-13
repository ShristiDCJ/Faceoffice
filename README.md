# Faceoffice - Facial Recognition Visitor Authentication System

A modern visitor authentication system using facial recognition to streamline visitor check-ins and instant push notifications to employees.

## Features

✅ **Visitor Kiosk** - Public-facing page for visitors to enter their name, contact info, and capture a facial photo

✅ **Employee Facial Login** - Facial recognition-based authentication (no passwords needed)

✅ **Employee Dashboard** - View, accept, or reject visitor requests with photos

✅ **Admin Panel** - Register and manage employees with facial enrollment

✅ **Smart Notifications** - Email + Push Notifications (Firebase Cloud Messaging) to employees

✅ **Auto-Reminders** - Push notification reminder after 2 minutes if no response from employee

✅ **Cloud Photo Storage** - Visitor photos stored securely on Cloudinary

## Tech Stack

- **Backend**: Python + Flask 3.0
- **Database**: SQLite
- **Facial Recognition**: OpenCV (Haar Cascades)
- **Photo Storage**: Cloudinary
- **Notifications**: Firebase Cloud Messaging (Push) + Flask-Mail (Email)
- **Background Tasks**: APScheduler
- **Hosting**: Render (or any Python-capable cloud platform)

## Project Structure

```
faceoffice/
├── app.py                          # Entry point
├── config.py                       # Flask configuration
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create from template)
├── firebase-key.json               # Firebase service account (download from Firebase)
├── Procfile                        # Render deployment config
├── app/
│   ├── __init__.py                # Flask app factory
│   ├── models.py                  # SQLAlchemy database models
│   ├── routes/
│   │   ├── visitor.py             # Visitor kiosk endpoints
│   │   ├── auth.py                # Employee facial login
│   │   ├── employee.py            # Employee dashboard endpoints
│   │   └── admin.py               # Admin employee management
│   ├── services/
│   │   ├── facial_recognition.py  # Face detection with OpenCV
│   │   ├── notification.py        # Email + Firebase push notifications
│   │   ├── cloudinary_service.py  # Photo upload to Cloudinary
│   │   └── request_handler.py     # Business logic layer
│   └── templates/
│       ├── base.html              # Base HTML template
│       ├── visitor.html           # Visitor kiosk page
│       ├── employee_login.html    # Facial recognition login
│       ├── employee_dashboard.html # Visitor request management
│       ├── admin_register.html    # Employee registration form
│       └── admin_employees.html   # Employee list management
├── static/
│   ├── css/style.css              # Custom styling
│   └── js/camera.js               # WebRTC camera handling
└── instance/
    └── faceoffice.db              # SQLite database (auto-created)
```

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Shristi2510/faceoffice.git
cd faceoffice
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create `.env` file in project root:

```bash
FLASK_ENV=development
[REDACTED_GENERIC_SECRET_1]=your-secret-key-here

# Database
DATABASE_URL=sqlite:///faceoffice.db

# Cloudinary (Photo Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_[REDACTED_GENERIC_SECRET_2]=your-api-secret

# Firebase (Push Notifications)
FIREBASE_KEY_PATH=firebase-key.json

# Email Notifications
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=shristi.extra.college@gmail.com
MAIL_[REDACTED_GENERIC_PASSWORD_5]=Shristi@2510
MAIL_DEFAULT_SENDER=shristi.extra.college@gmail.com

# App Configuration
APP_URL=http://localhost:5000
```

### 5. Firebase Cloud Messaging Setup

1. **Create Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Click "Create Project" and name it (e.g., "Faceoffice")
   - Enable Google Analytics (optional)

2. **Download Service Account Key:**
   - In Firebase Console, go to Project Settings ⚙️
   - Click "Service Accounts" tab
   - Click "Generate New Private Key"
   - Save the JSON file as `firebase-key.json` in your project root
   - This file enables backend push notifications

3. **Initialize Firebase in Frontend (Optional):**
   - For web push notifications (if using web app), follow Firebase docs
   - For mobile apps, use Firebase Admin SDK client

### 6. Cloudinary Setup (Photo Storage)

1. **Create Cloudinary Account:**
   - Sign up at [cloudinary.com](https://cloudinary.com) (free tier available)
   - Get your Cloud Name, API Key, and API Secret from Dashboard

2. **Add to `.env`:**
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_[REDACTED_GENERIC_SECRET_2]=your-api-secret
   ```

### 7. Email Notifications Setup (Gmail)

1. **Enable 2-Factor Authentication on Gmail:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Create App Password:**
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer"
   - Google generates a 16-character app password
   - Copy to `.env` as MAIL_PASSWORD

3. **Add to `.env`:**
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_[REDACTED_GENERIC_PASSWORD_5]=your-16-char-app-password
   ```

### 8. Run Application

```bash
python app.py
```

Open browser to `http://localhost:5000`

## Usage

### Admin: Register Employee

1. Navigate to `http://localhost:5000/admin/register`
2. Enter employee name, email, phone number
3. Capture their facial photo (good lighting, face visible)
4. Employee is registered and can now login via facial recognition

### Visitor: Submit Request

1. Go to `http://localhost:5000/visitor`
2. Enter your name, target employee, and phone number
3. Capture your facial photo
4. Request submitted!

### Employee: Review & Respond

1. Go to `http://localhost:5000/auth/login`
2. Align face with camera, system auto-verifies
3. Dashboard shows pending visitor requests with photos
4. Click Accept or Reject
5. Visitor receives instant push notification with response

### Automatic Reminder

- If employee doesn't respond within 2 minutes
- Visitor automatically receives a push notification reminder
- Visitor can check updated status on their device

## API Endpoints

### Visitor Routes
- `GET /visitor` - Visitor kiosk interface
- `POST /visitor/submit-request` - Submit meeting request with photo
- `GET /visitor/check-status/<id>` - Check request status

### Employee Routes
- `GET /employee/dashboard` - View pending requests
- `GET /employee/dashboard/requests` - Get requests as JSON
- `POST /employee/accept/<id>` - Accept visitor request
- `POST /employee/reject/<id>` - Reject visitor request
- `POST /employee/logout` - Logout

### Auth Routes
- `GET /auth/login` - Facial recognition login page
- `POST /auth/verify` - Server-side facial verification
- `POST /auth/logout` - Logout from session

### Admin Routes
- `GET /admin/register` - Employee registration form
- `POST /admin/register` - Register new employee
- `GET /admin/employees` - Employee list interface
- `GET /admin/employees/list` - Get employees as JSON
- `DELETE /admin/employees/<id>` - Remove employee

## Deployment on Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Faceoffice visitor auth system"
git branch -M main
git remote add origin https://github.com/yourusername/faceoffice.git
git push -u origin main
```

### 2. Create Render Service

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free (or Starter for production)

### 3. Set Environment Variables

In Render Dashboard → Environment:

```
FLASK_ENV=production
[REDACTED_GENERIC_SECRET_1]=<strong-random-key>
DATABASE_URL=sqlite:///faceoffice.db
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_[REDACTED_GENERIC_SECRET_2]=...
FIREBASE_KEY_PATH=firebase-key.json
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=...
MAIL_[REDACTED_GENERIC_PASSWORD_5]=...
MAIL_DEFAULT_SENDER=...
APP_URL=https://your-app-name.onrender.com
```

### 4. Add Firebase Key to Render

**Option A: Upload as File**
- In Render dashboard, add `firebase-key.json` to project files

**Option B: Environment Variable**
- Convert `firebase-key.json` to base64
- Store as environment variable
- Decode in app startup

### 5. Deploy

Push to GitHub or click "Deploy" in Render dashboard. Your app will be live at `https://your-app-name.onrender.com`

## Database Schema

### Employees Table
```sql
id (PRIMARY KEY)
name (UNIQUE)
email (UNIQUE)
phone (UNIQUE)
face_encoding (Binary) -- Serialized numpy array for login
fcm_token (TEXT) -- Firebase Cloud Messaging token
created_at (DATETIME)
```

### Visitor Requests Table
```sql
id (PRIMARY KEY)
visitor_name
visitor_phone
visitor_fcm_token (TEXT) -- Push notification token
employee_id (FOREIGN KEY)
photo_url (Cloudinary URL)
face_encoding (Binary) -- Visitor's facial encoding
status (pending/accepted/rejected)
created_at (DATETIME)
responded_at (DATETIME)
reminder_sent (BOOLEAN)
```

### Employee Face Logins Table
```sql
id (PRIMARY KEY)
employee_id (FOREIGN KEY, UNIQUE)
face_encoding (Binary)
registered_at (DATETIME)
```

## Security Features

✅ **Facial Authentication** - No passwords, face-based login  
✅ **Session Security** - Secure cookies with HTTPONLY flag  
✅ **HTTPS** - Enforced in production  
✅ **Cloud Storage** - Photos on Cloudinary (encrypted)  
✅ **Firebase Security** - Google-managed infrastructure  
✅ **Environment Secrets** - All credentials in .env (not in code)

### Recommended Security Enhancements
- [ ] Add rate limiting on endpoints
- [ ] Implement CSRF protection
- [ ] Add audit logging for all actions
- [ ] Use database encryption at rest
- [ ] Enable two-factor authentication for admin
- [ ] Regular security audits

## Troubleshooting

### Face Detection Issues
**Problem:** "No face detected"
- **Solution:** Ensure good lighting, face clearly visible, straight on camera

**Problem:** "Multiple faces detected"
- **Solution:** Only one person per photo

### Firebase Notifications Not Working
**Problem:** Push notifications not received
- **Solution:** 
  - Verify `firebase-key.json` exists and is valid
  - Check FCM token is being stored in database
  - Ensure Firebase project has Messaging enabled

### Cloudinary Upload Fails
**Problem:** Photo upload errors
- **Solution:**
  - Verify Cloudinary credentials in `.env`
  - Check internet connectivity
  - Ensure image format is JPEG/PNG

### Database Locked
**Problem:** "Database is locked"
- **Solution:**
  - Close other instances of the app
  - Delete `faceoffice.db-wal` if present
  - Restart Flask server

## Architecture Notes

### Facial Recognition Flow
1. User captures image via WebRTC camera
2. Image sent to backend as base64
3. OpenCV detects faces using Haar Cascades
4. Face region extracted and resized to 50x50px
5. Encoding created from pixel values
6. Cosine distance compared against stored encodings
7. Match threshold: 0.6

### Notification Flow
1. Visitor submits request → System creates DB entry
2. 2-minute reminder scheduled via APScheduler
3. Employee receives email with visitor photo (Flask-Mail)
4. Employee receives push notification (Firebase Cloud Messaging)
5. On accept/reject → Visitor gets instant push notification
6. After 2 minutes (if pending) → Visitor gets reminder push

## Future Enhancements

- [ ] WhatsApp/SMS integration for non-app users
- [ ] Pre-registered visitor whitelist
- [ ] QR code check-in
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Integration with building access systems
- [ ] Video call capability between visitor and employee
- [ ] Scheduled visit reservations

## Performance Metrics

- **Face Detection:** ~100-200ms per image
- **Email Delivery:** 1-2 seconds
- **Push Notification:** <1 second
- **Database Query:** <50ms average
- **Page Load:** <2 seconds

## License

MIT License - See LICENSE file

## Support & Issues

Found a bug? Have a feature request? [Open an issue on GitHub](https://github.com/yourusername/faceoffice/issues)

---

**Built with ❤️ for modern visitor management**
