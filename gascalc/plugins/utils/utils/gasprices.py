import http.client

conn = http.client.HTTPSConnection("api.collectapi.com")

headers = {
    'content-type': "application/json",
    'authorization': "apikey 3WMYkt1hxHXmRXq09QkFKw:4fsxzvltumEvMIMNwXlnqx"
    }
coords = {'LON':55.037053,
		'LAT':82.906731}
conn.request("GET", f"/gasPrice/fromCoordinates?lng={coords['LAT']}&lat={coords['LON']}", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))