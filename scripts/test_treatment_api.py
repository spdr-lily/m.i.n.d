"""Test treatment API endpoints."""
import requests

BASE = "http://localhost:8000/api/v1/treatment"
s = requests.Session()

r = s.post("http://localhost:8000/api/v1/auth/login", json={"username": "admin", "password": "admin"})
print("Login:", r.status_code)
token = r.json().get("access_token", "")
s.headers["Authorization"] = f"Bearer {token}"

r = s.get(f"{BASE}/associations", params={"limit": 3})
print("Associations:", r.status_code, r.json().get("total", 0))

r = s.get(f"{BASE}/stats/1")
data = r.json()
print("Stats TDM:", r.status_code, len(data.get("medication_stats", [])))
for m in data.get("medication_stats", [])[:5]:
    print(f'  {m["medication_name"]}: SR={m["success_rate"]}')

r = s.get("http://localhost:8000/api/v1/patients", params={"limit": 1})
patients = r.json().get("patients", [])
if patients:
    puuid = patients[0]["profile_uuid"]
    print(f"Patient UUID: {puuid}")
    r = s.post(f"{BASE}/predict", json={
        "patient_uuid": puuid,
        "disorder_id": 1,
        "medication_ids": [1, 2, 3],
    })
    print("Predict:", r.status_code)
    if r.status_code == 200:
        pred = r.json()
        print(f'  Disorder: {pred["disorder_name"]}')
        for p in pred["predictions"]:
            print(f'  {p["medication_name"]}: prob={p["success_probability"]}')
