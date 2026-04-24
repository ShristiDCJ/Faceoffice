# Faceoffice - Facial Recognition Visitor Authentication System

A modern visitor authentication system using facial recognition to streamline visitor check-ins and email notifications to employees.

## Features

✅ **Visitor Kiosk** - Public-facing page for visitors to enter their name, contact info, and capture a facial photo

✅ **Employee Facial Login** - Facial recognition-based authentication (no passwords needed)

✅ **Employee Password Login** - Alternative password-based login for employees

✅ **Employee Dashboard** - View, accept, or reject visitor requests with photos

✅ **Admin Panel** - Register and manage employees with facial enrollment

✅ **Admin Request Approval** - Admin can view all pending requests and approve/reject on behalf of employees

✅ **Smart Email Notifications** - Brevo SMTP email alerts to employees and visitors

✅ **Auto-Reminders** - Email reminder after 2 minutes if no response from employee

✅ **Cloud Photo Storage** - Visitor photos stored securely on Cloudinary

✅ **Firebase Realtime Database** - Primary data store for employees and visitor requests (SQLite as backup)

## Tech Stack

- **Backend**: Python + Flask 3.0
- **Database**: Firebase Realtime Database (primary), SQLite (local backup)
- **Facial Recognition**: OpenCV (Haar Cascades)
- **Photo Storage**: Cloudinary
- **Email Notifications**: Brevo SMTP (via `email_service.py`) + Flask-Mail (legacy)
- **Background Tasks**: APScheduler (2-minute email reminders)
- **Hosting**: Render (or any Python-capable cloud platform)

## Project Structure

```
faceoffice/
├── app.py                          # Entry point
├── wsgi.py                         # WSGI entry for production
├── config.py                       # Flask configuration (dev/prod/test)
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create from template)
├── firebase-key.json               # Firebase service account (download from Firebase)
├── Procfile                        # Render deployment config
├── init_db.py                      # Initialize SQLite database
├── test_email_flow.py              # Email flow test script
├── EMAIL_TESTING_GUIDE.md          # Email testing documentation
├── app/
│   ├── __init__.py                # Flask app factory
│   ├── models.py                  # SQLAlchemy database models
│   ├── routes/
│   │   ├── __init__.py            # Blueprint definitions
│   │   ├── visitor.py             # Visitor kiosk endpoints
│   │   ├── auth.py                # Employee face + password login
│   │   ├── employee.py            # Employee dashboard endpoints
│   │   └── admin.py               # Admin employee & request management
│   ├── services/
│   │   ├── facial_recognition.py  # Face detection with OpenCV
│   │   ├── email_service.py       # Brevo SMTP email sender
│   │   ├── notification.py        # Flask-Mail email + APScheduler reminders
│   │   ├── cloudinary_service.py  # Photo upload to Cloudinary
│   │   ├── firebase_service.py    # Firebase Realtime DB CRUD
│   │   ├── firebase_request_handler.py  # Request lifecycle + Brevo emails
│   │   └── request_handler.py     # Legacy SQLite request handler
│   └── templates/
│       ├── base.html              # Base HTML template
│       ├── visitor.html           # Visitor kiosk page
│       ├── employee_login.html    # Face + password login tabs
│       ├── employee_dashboard.html # Visitor request management
│       ├── admin_register.html    # Employee registration form (with password)
│       ├── admin_employees.html   # Employee list management
│       └── admin_requests.html    # Admin pending requests approval
├── static/
│   ├── css/style.css              # Custom styling
│   └── js/camera.js               # WebRTC camera handling
│   └── js/dashboard.js            # Dashboard interactions
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
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///faceoffice.db

# Cloudinary (Photo Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Firebase Realtime Database
FIREBASE_KEY_PATH=firebase-key.json
FIREBASE_DB_URL=https://your-project-default-rtdb.firebaseio.com

# Brevo SMTP (Primary Email)
BREVO_API_KEY=your-brevo-api-key
MAIL_FROM_EMAIL=noreply@faceoffice.com

# Flask-Mail / Legacy SMTP (Optional fallback)
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-brevo-api-key
MAIL_DEFAULT_SENDER=noreply@faceoffice.com

# App Configuration
APP_URL=http://localhost:5000

# Admin Panel Password (change in production!)
ADMIN_PASSWORD=admin-change-in-production
```

### 5. Firebase Realtime Database Setup

1. **Create Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Click "Create Project" and name it (e.g., "Faceoffice")
   - Enable Google Analytics (optional)

2. **Enable Realtime Database:**
   - In Firebase Console, go to "Build" → "Realtime Database"
   - Click "Create Database"
   - Choose "Start in test mode" (or set security rules for production)
   - Copy the database URL (e.g., `https://your-project-default-rtdb.firebaseio.com`)

3. **Download Service Account Key:**
   - In Firebase Console, go to Project Settings ⚙️
   - Click "Service Accounts" tab
   - Click "Generate New Private Key"
   - Save the JSON file as `firebase-key.json` in your project root
   - This file enables backend access to Realtime Database

### 6. Cloudinary Setup (Photo Storage)

1. **Create Cloudinary Account:**
   - Sign up at [cloudinary.com](https://cloudinary.com) (free tier available)
   - Get your Cloud Name, API Key, and API Secret from Dashboard

2. **Add to `.env`:**
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

### 7. Brevo Email Setup

1. **Create Brevo Account:**
   - Sign up at [brevo.com](https://www.brevo.com) (free tier available)
   - Go to "SMTP & API" → "API Keys"
   - Generate an API key

2. **Add to `.env`:**
   ```
   BREVO_API_KEY=your-brevo-api-key
   MAIL_FROM_EMAIL=noreply@faceoffice.com
   ```

3. **Sender Verification:**
   - In Brevo dashboard, verify your sender domain or email address
   - Without verification, emails may land in spam

### 8. Initialize Database

```bash
python init_db.py
```

This creates the SQLite tables (`employees`, `visitor_requests`, `employee_face_logins`).

### 9. Run Application

```bash
python app.py
```

Open browser to `http://localhost:5000`

## Usage

### Admin: Register Employee

1. Navigate to `http://localhost:5000/admin/register`
2. Enter employee name, email, phone number, and password (min 8 characters)
3. Capture their facial photo (good lighting, face visible)
4. Employee is registered in both Firebase and SQLite
5. Employee can now login via facial recognition or password

### Visitor: Submit Request

1. Go to `http://localhost:5000/visitor`
2. Enter your name, target employee name, email, and phone number
3. Capture your facial photo
4. Request submitted! Employee receives an email notification instantly

### Employee: Review & Respond

1. Go to `http://localhost:5000/auth/login`
2. Choose login method:
   - **Face Recognition tab**: Align face with camera, system auto-verifies
   - **Password tab**: Enter email and password
3. Dashboard shows pending visitor requests with photos
4. Click Accept or Reject
5. Visitor receives an email with the response

### Admin: Manage Pending Requests

1. Navigate to `http://localhost:5000/admin/requests`
2. View all pending visitor requests across all employees
3. Click Accept or Reject on behalf of an employee
4. Both visitor and employee receive email confirmations

### Automatic Reminder

- If employee doesn't respond within 2 minutes
- Employee automatically receives a reminder email
- Employee can then accept/reject from the dashboard

## API Endpoints

### Visitor Routes
- `GET /visitor` - Visitor kiosk interface
- `POST /visitor/submit-request` - Submit meeting request with photo
- `GET /visitor/check-status/<id>` - Check request status

### Auth Routes
- `GET /auth/login` - Employee login page (face + password tabs)
- `POST /auth/verify` - Server-side facial verification
- `POST /auth/login/password` - Password-based login
- `POST /auth/logout` - Logout from session

### Employee Routes
- `GET /employee/dashboard` - View pending requests
- `GET /employee/dashboard/requests` - Get requests as JSON
- `POST /employee/accept/<id>` - Accept visitor request
- `POST /employee/reject/<id>` - Reject visitor request
- `POST /employee/logout` - Logout

### Admin Routes
- `GET /admin/register` - Employee registration form
- `POST /admin/register` - Register new employee
- `GET /admin/employees` - Employee list interface
- `GET /admin/employees/list` - Get employees as JSON
- `DELETE /admin/employees/<id>` - Remove employee
- `GET /admin/requests` - Admin pending requests page
- `GET /admin/requests/list` - Get all pending requests (API)
- `POST /admin/requests/<id>/accept` - Admin accepts request on behalf of employee
- `POST /admin/requests/<id>/reject` - Admin rejects request on behalf of employee

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
   - **Start Command:** `gunicorn wsgi:application` (or `gunicorn app:app`)
   - **Instance Type:** Free (or Starter for production)

### 3. Set Environment Variables

In Render Dashboard → Environment:

```
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=sqlite:///faceoffice.db
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
FIREBASE_KEY_PATH=firebase-key.json
FIREBASE_DB_URL=https://your-project-default-rtdb.firebaseio.com
BREVO_API_KEY=...
MAIL_FROM_EMAIL=noreply@faceoffice.com
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=...
MAIL_DEFAULT_SENDER=...
APP_URL=https://your-app-name.onrender.com
ADMIN_PASSWORD=<change-me>
```

### 4. Add Firebase Key to Render

**Option A: Upload as File**
- In Render dashboard, add `firebase-key.json` to project files

**Option B: Environment Variable (Base64)**
- Convert `firebase-key.json` to base64
- Store as environment variable
- Decode in app startup

### 5. Deploy

Push to GitHub or click "Deploy" in Render dashboard. Your app will be live at `https://your-app-name.onrender.com`

## Database Schema

### Employees Table (SQLite)
```sql
id (PRIMARY KEY)
name (UNIQUE)
email (UNIQUE)
phone (UNIQUE)
password_hash (TEXT) -- Werkzeug hashed password
face_encoding (Binary) -- Serialized numpy array for login
created_at (DATETIME)
```

### Visitor Requests Table (SQLite)
```sql
id (PRIMARY KEY)
visitor_name
visitor_phone
visitor_email (TEXT) -- Required for email confirmations
employee_id (FOREIGN KEY)
photo_url (Cloudinary URL)
face_encoding (Binary) -- Visitor's facial encoding
status (pending/accepted/rejected)
created_at (DATETIME)
responded_at (DATETIME)
reminder_sent (BOOLEAN)
```

### Employee Face Logins Table (SQLite)
```sql
id (PRIMARY KEY)
employee_id (FOREIGN KEY, UNIQUE)
face_encoding (Binary)
registered_at (DATETIME)
```

### Firebase Realtime Database Structure
```json
{
  "employees": {
    "<firebase_id>": {
      "name": "...",
      "email": "...",
      "phone": "...",
      "face_encoding": "<base64>",
      "created_at": "..."
    }
  },
  "visitor_requests": {
    "<request_id>": {
      "visitor_name": "...",
      "visitor_email": "...",
      "visitor_phone": "...",
      "employee_id": "<firebase_employee_id>",
      "photo_url": "...",
      "face_encoding": "<base64>",
      "status": "pending",
      "created_at": "...",
      "responded_at": null,
      "reminder_sent": false
    }
  }
}
```

## Security Features

✅ **Facial Authentication** - No passwords required for face-based login  
✅ **Password Hashing** - Werkzeug `generate_password_hash` for password storage  
✅ **Session Security** - Secure cookies with HTTPONLY flag  
✅ **HTTPS** - Enforced in production  
✅ **Cloud Storage** - Photos on Cloudinary (encrypted at rest)  
✅ **Environment Secrets** - All credentials in `.env` (not in code)

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

### Email Notifications Not Working
**Problem:** Emails not received
- **Solution:**
  - Verify `BREVO_API_KEY` is set correctly
  - Check sender email is verified in Brevo dashboard
  - Review application logs for SMTP errors
  - Ensure `MAIL_FROM_EMAIL` matches a verified sender

### Cloudinary Upload Fails
**Problem:** Photo upload errors
- **Solution:**
  - Verify Cloudinary credentials in `.env`
  - Check internet connectivity
  - Ensure image format is JPEG/PNG

### Firebase Connection Issues
**Problem:** "Firebase initialization failed"
- **Solution:**
  - Verify `firebase-key.json` exists and is valid
  - Check `FIREBASE_DB_URL` is correct
  - Ensure Firebase Realtime Database is created and rules allow access

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

### Visitor Request Flow (Firebase + Brevo)
```
1. VISITOR SUBMITS REQUEST
   → Upload photo to Cloudinary
   → Create request in Firebase Realtime Database
   → Backup to SQLite (optional)
   → EMAIL #1: "New Visitor Alert" to Employee (Brevo SMTP)
   → SCHEDULE: 2-minute reminder email (APScheduler)

2. EMPLOYEE ACCEPTS (within 2 min)
   → Cancel reminder
   → Update status to 'accepted' in Firebase
   → EMAIL #2: "Request Accepted" to Visitor
   → EMAIL #3: "Confirmation" to Employee

3. EMPLOYEE REJECTS (within 2 min)
   → Cancel reminder
   → Update status to 'rejected' in Firebase
   → EMAIL #4: "Request Declined" to Visitor
   → EMAIL #5: "Confirmation" to Employee

4. NO RESPONSE (2 min elapsed)
   → EMAIL #6: "Reminder: Pending Visitor" to Employee
   → Employee can then accept/reject (emails #2-5)
```

### Admin Request Approval Flow
```
ADMIN OPENS /admin/requests
   → Fetch all pending requests from Firebase
   → Display with visitor photo, employee name/email
   → Admin clicks Accept/Reject
   → Same email flow as employee action (visitor + employee notified)
```

## Email Types Summary

| Email | Recipient | Trigger | Content |
|-------|-----------|---------|---------|
| New Visitor Alert | Employee | Request submitted | Visitor details, photo, dashboard link |
| Pending Reminder | Employee | 2 minutes passed | Reminder with dashboard link |
| Acceptance Confirmation | Visitor | Employee/Admin accepts | Proceed to meet them |
| Acceptance Confirmation | Employee | Employee/Admin accepts | Confirmation of acceptance |
| Rejection Notice | Visitor | Employee/Admin rejects | Request declined, contact security |
| Rejection Confirmation | Employee | Employee/Admin rejects | Confirmation of rejection |

## Testing

### Run Email Flow Test
```bash
python test_email_flow.py
```

### Local Testing with MailHog
```bash
# Start MailHog
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Configure .env for MailHog
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False

# View emails at http://localhost:8025
```

See `EMAIL_TESTING_GUIDE.md` for complete testing documentation.

## Performance Metrics

- **Face Detection:** ~100-200ms per image
- **Email Delivery:** 1-2 seconds (Brevo SMTP)
- **Database Query:** <50ms average
- **Page Load:** <2 seconds

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

## License

MIT License - See LICENSE file

## Support & Issues

Found a bug? Have a feature request? [Open an issue on GitHub](https://github.com/yourusername/faceoffice/issues)

---

**Built with ❤️ for modern visitor management**

