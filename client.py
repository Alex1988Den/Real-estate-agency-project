import requests
import json

def get_token():
    url = "http://localhost:8000/token"
    response = requests.post(url, data={"username": "user", "password": "password"})
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        raise Exception("Could not obtain token")

def make_prediction(data):
    token = get_token()
    url = "http://localhost:8000/predict/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["prediction"]
    else:
        raise Exception(f"Request failed with status code {response.status_code}")

if __name__ == "__main__":
    data = {
        "baths": 2,
        "beds": 3,
        "stories": 2,
        "sqft": 2000
    }
    try:
        prediction = make_prediction(data)
        print(f"Prediction: {prediction}")
    except Exception as e:
        print(f"Error: {e}") 
