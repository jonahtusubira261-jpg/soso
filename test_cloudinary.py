#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soso_config.settings')
django.setup()

# Import after Django setup
from django.conf import settings
import cloudinary
import cloudinary.api
import cloudinary.uploader

def test_cloudinary():
    print("🔍 Testing Cloudinary Connection...\n")
    
    # 1. Check settings
    print("1. Checking Settings:")
    try:
        cloud_name = settings.CLOUDINARY_STORAGE['CLOUD_NAME']
        api_key = settings.CLOUDINARY_STORAGE['API_KEY']
        api_secret = settings.CLOUDINARY_STORAGE['API_SECRET'][:5] + '...'  # Hide secret
        
        print(f"   ✅ Cloud Name: {cloud_name}")
        print(f"   ✅ API Key: {api_key[:5]}...")
        print(f"   ✅ API Secret: {api_secret}")
    except Exception as e:
        print(f"   ❌ Settings Error: {e}")
        return False
    
    # 2. Test API connection
    print("\n2. Testing API Connection:")
    try:
        # Try to get account info (requires API access)
        result = cloudinary.api.ping()
        print(f"   ✅ Connected! Status: {result.get('status', 'OK')}")
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")
        return False
    
    # 3. Test upload
    print("\n3. Testing Upload:")
    try:
        # Create a simple test file
        test_content = b"test image data"
        with open('test_upload.txt', 'wb') as f:
            f.write(test_content)
        
        # Upload
        result = cloudinary.uploader.upload(
            'test_upload.txt',
            folder='test_folder',
            public_id='test_file'
        )
        
        print(f"   ✅ Upload Successful!")
        print(f"   📍 URL: {result['url']}")
        print(f"   🆔 Public ID: {result['public_id']}")
        
        # Clean up
        os.remove('test_upload.txt')
        
        # 4. Test delete
        print("\n4. Testing Delete:")
        cloudinary.uploader.destroy(result['public_id'])
        print("   ✅ Delete Successful!")
        
    except Exception as e:
        print(f"   ❌ Upload Failed: {e}")
        return False
    
    print("\n✅ All Cloudinary tests passed!")
    return True

if __name__ == '__main__':
    success = test_cloudinary()
    sys.exit(0 if success else 1)