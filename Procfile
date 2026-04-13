web: gunicorn app:application
worker: python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.services.notification import start_scheduler; start_scheduler(); import time; time.sleep(86400)"
