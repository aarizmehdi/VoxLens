import httpx

url = 'https://voxlens-backend-ke9v.onrender.com'
res = httpx.get(f'{url}/api/meetings?limit=100')
meetings = res.json().get('meetings', [])
count = 0
for m in meetings:
    httpx.delete(f'{url}/api/meetings/{m["id"]}')
    count += 1
print(f'Successfully deleted {count} meetings from the live database!')
