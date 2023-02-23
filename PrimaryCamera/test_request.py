import requests
res = requests.post('http://localhost:5000/camera', json={"motor_p":45})
if res.ok:
    print(res.json())
else:
    print(res.text)