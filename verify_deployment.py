import requests
import sys

try:
    response = requests.get('https://twistergem-3rs6ph.stormkit.dev/api/health', timeout=10)
    if response.status_code == 200:
        print("â AINEXUS Deployment Successful!")
        print(f"í³ Response: {response.json()}")
        sys.exit(0)
    else:
        print(f"â Deployment Issue: Status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"â Deployment Failed: {e}")
    sys.exit(1)
