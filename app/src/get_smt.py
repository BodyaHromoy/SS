import requests

resp = requests.get('http://192.168.1.16:8080/api/dev/866011056062144')
lines = {i: bool(resp.json()['DigitalIn1'] & (1<<i)) for i in range(3)}
print(lines)