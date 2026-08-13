from curl_cffi import requests
from requests_futures.sessions import FuturesSession

session = requests.Session(impersonate="chrome120")
fs = FuturesSession(session=session)
f = fs.get('https://example.com')
r = f.result()
print(r.status_code)
