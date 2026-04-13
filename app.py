import os
from app import create_app

application = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000)
