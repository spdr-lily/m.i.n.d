"""Test prediction endpoint."""
import requests as r
s = r.Session()
resp = s.post("http://localhost:8000/api/v1/auth/login", json={"username":"admin","password":"admin"})
s.headers["Authorization"] = "Bearer " + resp.json()["access_token"]

r2 = s.get("http://localhost:8000/api/v1/patients", params={"limit": 1})
puuid = r2.json()["patients"][0]["patient_uuid"]
print("Patient:", puuid)

r3 = s.post("http://localhost:8000/api/v1/treatment/predict", json={
    "patient_uuid": puuid,
    "disorder_id": 1,
    "medication_ids": [1, 2, 3]
})
print("Status:", r3.status_code)
data = r3.json()
print("Disorder:", data["disorder_name"])
for p in data["predictions"]:
    print(f'  {p["medication_name"]}: prob={p["success_probability"]}')
