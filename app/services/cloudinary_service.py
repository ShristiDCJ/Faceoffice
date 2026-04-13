import cloudinary
import cloudinary.uploader
import os
import base64
from dotenv import load_dotenv
import urllib3
import requests
import ssl
import hashlib
import time

# Disable SSL verification globally for development
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

def initialize_cloudinary():
    """Initialize Cloudinary with environment config"""
    try:
        config = {}
        for key, value in os.environ.items():
            if key == 'CLOUDINARY_CLOUD_NAME':
                config['cloud_name'] = value
            elif key == 'CLOUDINARY_API_KEY':
                config['api_key'] = value
            elif 'CLOUDINARY_API' in key and 'SECRET' in key.upper():
                config['api_secret'] = value

        if not all(k in config for k in ('cloud_name', 'api_key')):
            raise ValueError("Missing Cloudinary credentials")

        cloudinary.config(**config)
        return True

    except Exception as e:
        print(f"Cloudinary Error: {e}")
        return False

def upload_photo(base64_image, folder='visitor_photos'):
    """Upload base64 image to Cloudinary"""
    try:
        # Get credentials
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')


        # Scan for API secret
        api_secret = None
        for key, value in os.environ.items():
            if "CLOUDINARY_API" in key and "SECRET" in key.upper():
                api_secret = value
                break

        if not cloud_name or not api_key:
            raise ValueError("Missing credentials")

        # Decode image
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]

        image_data = base64.b64decode(base64_image)

        # HTTP upload to Cloudinary
        upload_url = f'https://api.cloudinary.com/v1_1/{cloud_name}/image/upload'

        files = {'file': ('image.jpg', image_data, 'image/jpeg')}
        data = {
            'api_key': api_key,
            'folder': folder,
            'timestamp': str(int(time.time()))
        }

        # Sign if secret available
        if api_secret:
            params = '&'.join(sorted([f'{k}={v}' for k, v in data.items() if k != 'api_key']))
            to_sign = f'{params}{api_secret}'
            data['signature'] = hashlib.sha1(to_sign.encode()).hexdigest()

        response = requests.post(upload_url, files=files, data=data, verify=False)

        if response.status_code == 200:
            url = response.json().get('secure_url')
            print(f"Uploaded: {url}")
            return url, None
        else:
            error = response.json().get('error', {}).get('message', str(response.status_code))
            return None, error

    except Exception as e:
        print(f"Upload error: {e}")
        return None, str(e)

def delete_photo(public_id):
    """Delete photo from Cloudinary"""
    try:
        initialize_cloudinary()
        cloudinary.uploader.destroy(public_id)
        return True, None
    except Exception as e:
        return False, str(e)
