import urllib.request
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "devacia_wolf_2025"

def run_test(name, func):
    try:
        func()
        print(f"[PASS] {name}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        # sys.exit(1) # Don't exit, run all tests

def make_request(endpoint, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method=method)
    
    for k, v in headers.items():
        req.add_header(k, v)
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
        req.data = json_data
        
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def test_auth_fail():
    status, _ = make_request("/crm/get-leads")
    assert status == 403, f"Expected 403, got {status}"

def test_auth_wrong_key():
    status, _ = make_request("/crm/get-leads", headers={"x-api-key": "wrong"})
    assert status == 403, f"Expected 403, got {status}"

def test_add_lead():
    payload = {
        "name": "John Doe",
        "company": "Acme Corp",
        "pain_point": "Low sales",
        "status": "Lead",
        "notes": "Interested in AI"
    }
    status, resp = make_request("/crm/add-lead", method="POST", data=payload, headers={"x-api-key": API_KEY})
    assert status == 200, f"Expected 200, got {status}"
    assert resp["name"] == "John Doe"

def test_get_leads():
    status, resp = make_request("/crm/get-leads", headers={"x-api-key": API_KEY})
    assert status == 200, f"Expected 200, got {status}"
    assert len(resp) > 0
    assert resp[0]["name"] == "John Doe"

def test_save_script():
    payload = {
        "client_name": "John Doe",
        "title": "Cold Email",
        "content": "Hello John...",
        "tone": "Wolf"
    }
    status, resp = make_request("/vault/save-script", method="POST", data=payload, headers={"x-api-key": API_KEY})
    assert status == 200, f"Expected 200, got {status}"
    assert resp["title"] == "Cold Email"

def test_get_latest_script():
    status, resp = make_request("/vault/get-latest-script", headers={"x-api-key": API_KEY})
    assert status == 200, f"Expected 200, got {status}"
    assert resp["title"] == "Cold Email"

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(5) # Give server time to start
    
    run_test("Auth Fail (No Key)", test_auth_fail)
    run_test("Auth Fail (Wrong Key)", test_auth_wrong_key)
    run_test("Add Lead", test_add_lead)
    run_test("Get Leads", test_get_leads)
    run_test("Save Script", test_save_script)
    run_test("Get Latest Script", test_get_latest_script)
