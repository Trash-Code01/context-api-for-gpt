import urllib.request
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "devacia_wolf_2025"

def run_test(name, func):
    try:
        func()
        print(f"[PASS] {name}")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")

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

def test_research():
    # Note: This might fail if google blocks the request, but we test the endpoint logic
    payload = {"client_name": "OpenAI"} # Use a known entity
    # The endpoint expects query param for client_name? No, the code says:
    # def agent_research(client_name: str): -> Query param by default in FastAPI if not Body
    # Wait, in the implementation:
    # @app.post("/agent/research")
    # def agent_research(client_name: str):
    # This means it expects a query parameter `?client_name=...`
    
    status, resp = make_request("/agent/research?client_name=OpenAI", method="POST", headers={"x-api-key": API_KEY})
    
    if status != 200:
        print(f"Research failed with status {status}: {resp}")
        raise Exception(f"Status {status}")
        
    assert "pdf" in resp
    print(f"  PDF created at: {resp['pdf']}")
    assert os.path.exists(resp['pdf'])

def test_contract():
    # Expects query params: client_name, service_name, price
    params = "client_name=Acme&service_name=WebDev&price=$5000"
    status, resp = make_request(f"/agent/create-contract?{params}", method="POST", headers={"x-api-key": API_KEY})
    
    if status != 200:
        print(f"Contract failed with status {status}: {resp}")
        raise Exception(f"Status {status}")
        
    assert "pdf" in resp
    print(f"  PDF created at: {resp['pdf']}")
    assert os.path.exists(resp['pdf'])

def test_send_email_fail():
    # This should fail because credentials are placeholders
    params = "client_email=test@example.com&client_name=Acme&doc_type=contract"
    status, resp = make_request(f"/agent/send-packet?{params}", method="POST", headers={"x-api-key": API_KEY})
    
    # Expect 500 because email sending fails
    assert status == 500, f"Expected 500 (Email Fail), got {status}"

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(5)
    
    run_test("Agent Research", test_research)
    run_test("Agent Contract", test_contract)
    run_test("Agent Email (Expected Fail)", test_send_email_fail)
