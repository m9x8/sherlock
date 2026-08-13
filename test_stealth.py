import asyncio
from sherlock_project.stealth_engine import StealthEngine

async def test():
    async with StealthEngine() as engine:
        r = await engine.request('GET', 'https://tls.browserleaks.com/json')
        print(f"[{engine.impersonate}]")
        print(r.json().get('ja4'))
        print(r.json().get('akamai_text'))

asyncio.run(test())
