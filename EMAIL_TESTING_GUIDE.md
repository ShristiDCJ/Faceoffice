# Email Notification Testing Guide

## Overview

The Faceoffice system has been fully converted to use **email-only notifications**. All Firebase push notification code has been removed, making the system simpler and easier to deploy.

## Email Flow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   VISITOR SUBMISSION                          │
└──────────────┬───────────────────────────────────────────────┘
               │
               ├─→ Create VisitorRequest in database
               ├─→ Upload photo to Cloudinary
               ├─→ Email: Send "New Visitor Alert" to Employee
               └─→ Schedule: 2-minute reminder email
                    │
                    ├─→ If Employee accepts (within 2 min)
                    │   ├─→ Cancel reminder
                    │   ├─→ Email: "Request Accepted ✓" to Visitor
                    │   └─→ Email: "Confirmation" to Employee
                    │
                    └─→ If no response (2 min elapsed)
                        └─→ Email: "Reminder: Pending Visitor" to Employee
```

## Email Types

### 1. New Visitor Alert (Employee)
**When:** Immediately upon visitor request submission
**Recipients:** Employee only
**Content:**
- Visitor name
- Visitor photo (embedded)
- Link to employee dashboard to accept/reject
- Note about 2-minute response window

### 2. 2-Minute Reminder (Employee)
**When:** 2 minutes after request submission (if no response)
**Recipients:** Employee only
**Content:**
- Reminder that visitor is still waiting
- Link to dashboard
- Visitor name

### 3. Request Accepted (Both)
**When:** When employee accepts the request
**Recipients:** Visitor & Employee
**Content:**
- Visitor: Confirmation to proceed
- Employee: Confirmation of acceptance with visitor email

### 4. Request Rejected (Both)
**When:** When employee rejects the request
**Recipients:** Visitor & Employee
**Content:**
- Visitor: Decline notice with contact security option
- Employee: Confirmation of rejection with visitor email

## Testing the Email Flow

### Method 1: Run the Test Script

```bash
python test_email_flow.py
```

This will:
- Create a test employee
- Simulate a visitor request
- Test acceptance and rejection flows
- Verify all email templates are generated correctly
- Display a comprehensive summary

### Method 2: Manual Testing with MailHog (Recommended)

MailHog allows you to test emails locally without sending real emails.

#### Setup MailHog

```bash
# Download and run MailHog
# Windows: Download from https://github.com/mailhog/MailHog/releases
# Or use Docker:
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

#### Configure .env for MailHog

```env
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=test
MAIL_PASSWORD=test
MAIL_DEFAULT_SENDER=test@faceoffice.local
```

#### View Captured Emails

Open browser: `http://localhost:8025`

You'll see all emails sent by the application, with full HTML preview.

### Method 3: Real Email Testing (Gmail)

To test with real Gmail addresses (requires 2FA setup):

#### 1. Enable 2-Factor Authentication
- Go to: `https://myaccount.google.com/security`
- Enable 2-Step Verification

#### 2. Generate App Password
- Go to: `https://myaccount.google.com/apppasswords`
- Select "Mail" and "Windows Computer"
- Copy the 16-character password

#### 3. Update .env

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=<16-char-app-password>
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

#### 4. Test Email Sending (Python)

```python
from app import create_app
from app.services.notification import send_email

app = create_app()
with app.app_context():
    success, error = send_email(
        "recipient@example.com",
        "Test Subject",
        "<h1>Test Email</h1><p>This is a test email.</p>"
    )
    if success:
        print("✓ Email sent successfully!")
    else:
        print(f"✗ Error: {error}")
```

## Removed Firebase Dependencies

The following have been removed from the codebase:

### Files Modified
- `app/models.py` - Removed `fcm_token` fields
- `app/services/notification.py` - Removed Firebase code, kept email functions
- `app/services/request_handler.py` - Updated function signatures
- `config.py` - Removed Firebase configuration

### Code Removed
```python
# REMOVED: Firebase Admin SDK imports and initialization
import firebase_admin
from firebase_admin import credentials, messaging

# REMOVED: Functions that only send push notifications
def notify_visitor_request_accepted(visitor_fcm_token, employee_name)
def notify_visitor_request_rejected(visitor_fcm_token, employee_name)
def send_visitor_reminder(visitor_fcm_token, employee_name)

# REMOVED: Database fields
Employee.fcm_token  # Firebase token for employees
VisitorRequest.visitor_fcm_token  # Firebase token for visitors

# REMOVED: Firebase key requirement
firebase-key.json  # No longer needed
```

## Step-by-Step Email Flow Test

### Step 1: Start Application
```bash
python app.py
# Server running on http://localhost:5000
```

### Step 2: Open Visitor Kiosk
```
http://localhost:5000/visitor
```

### Step 3: Fill Visitor Form
- Name: "Test Visitor"
- Contact Employee: (registered employee name)
- Email: "visitor@example.com"
- Phone: "555-1234"
- Capture photo

✓ **Email 1 Sent:** "New Visitor: Test Visitor" to employee

### Step 4: Employee Accepts Request
- Go to employee login: `http://localhost:5000/auth/login`
- Face recognition login
- Accept on dashboard

✓ **Email 2 Sent:** "Request Accepted ✓" to visitor
✓ **Email 3 Sent:** "Confirmation" to employee

### Step 5: Wait for 2-Minute Reminder
Create another visitor request and wait 2 minutes without accepting/rejecting

✓ **Email 4 Sent:** "Reminder: Pending Visitor Request" to employee (after 2 min)

### Step 6: Employee Rejects Request
Create another visitor request and reject it

✓ **Email 5 Sent:** "Request Declined" to visitor
✓ **Email 6 Sent:** "Confirmation" to employee

## Troubleshooting

### Emails Not Sending

**Problem:** No emails received

**Solution:**
1. Check `.env` configuration:
   ```bash
   # Verify these are set
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=(your email)
   MAIL_PASSWORD=(your app password)
   ```

2. Check Flask-Mail is installed:
   ```bash
   pip list | grep Flask-Mail
   ```

3. Check logs for errors:
   ```python
   # Look for "Failed to send email" in logs
   ```

### 2-Minute Reminder Not Working

**Problem:** Reminder email not sent after 2 minutes

**Solution:**
1. Check APScheduler is running:
   ```python
   # Added to logs on startup:
   # "APScheduler started for reminder tasks"
   ```

2. Keep application running (scheduler runs in background)

3. Check reminder was scheduled:
   ```python
   # Logs should show:
   # "Reminder scheduled for request X"
   ```

### Database Issues

**Problem:** "Database is locked" error

**Solution:**
```bash
# Stop all Python processes
# Delete lock files
rm instance/faceoffice.db-wal
rm instance/faceoffice.db-shm

# Restart application
python app.py
```

## Email Configuration for Different Providers

### Gmail (with 2FA)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=<16-char-app-password>
```

### Microsoft Outlook
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### SendGrid
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=<sendgrid-api-key>
```

### AWS SES
```env
MAIL_SERVER=email-smtp.<region>.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<ses-smtp-username>
MAIL_PASSWORD=<ses-smtp-password>
```

## Deployment Notes

### Render Deployment

1. Remove `firebase-key.json` (no longer needed)
2. Add email credentials to environment variables:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=...
   MAIL_PASSWORD=...
   ```
3. App will start scheduler on deploy
4. Emails will be sent in background

### Environment Checklist

- [x] Removed Firebase dependencies
- [x] Email configuration set in .env
- [x] APScheduler for 2-minute reminders
- [x] VisitorRequest updated (no fcm_token)
- [x] Employee updated (no fcm_token)
- [x] All email templates complete
- [x] Error handling for failed emails
- [x] Logging enabled for debugging

## Verification Commands

```bash
# Check for any remaining Firebase references
grep -r "firebase" --include="*.py" app/

# Check models are updated
grep -r "fcm_token" --include="*.py" app/

# Should return: 0 results if everything is clean

# Verify email functions exist
grep -r "def send_" --include="*.py" app/services/notification.py

# Should show: send_email, send_visitor_acceptance_email, send_visitor_rejection_email, send_employee_pending_reminder_email, notify_employee_visitor_arrived
```

## Success Indicators

✓ Visitor can submit request with email
✓ Employee receives immediate email notification
✓ Employee receives 2-minute reminder if no response
✓ Employee can accept/reject with confirmation emails sent
✓ Application starts without Firebase errors
✓ No `firebase-key.json` required
✓ All emails contain proper HTML formatting
✓ Links in emails work correctly
✓ Database stores visitor_email successfully
✓ Reminders are cancelled when request is accepted/rejected

## Support

For issues with email configuration or testing:
1. Check logs for specific errors
2. Verify .env file has correct credentials
3. Test with MailHog first (local testing)
4. Use Gmail app passwords (not account password)
5. Check sender email is authorized in mail server
