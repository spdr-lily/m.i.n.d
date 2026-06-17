"""Test treatment API."""
import requests as r
s = r.Session()
resp = s.post("http://localhost:8000/api/v1/auth/login", json={"username":"admin","password":"admin"})
s.headers["Authorization"] = "Bearer " + resp.json()["access_token"]

resp2 = s.get("http://localhost:8000/api/v1/treatment/stats/1")
print("Status:", resp2.status_code)
print("Body:", resp2.text[:300])
