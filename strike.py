import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8181/user/login"
HEADERS = {"X-API-KEY": "alpha-squad-77"}
# Add the required body payload!
PAYLOAD = {"email": "test@hideout.com", "password": "securepass"}

def send_request(req_id):
    try:
        # Pass the json payload here
        response = requests.post(URL, headers=HEADERS, json=PAYLOAD, timeout=5)
        print(f"Request {req_id:02d}: {response.status_code}")
    except Exception as e:
        print(f"Request {req_id:02d}: Failed - {e}")

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(send_request, range(1, 21))