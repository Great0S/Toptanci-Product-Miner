from datetime import datetime
import asyncio


import aiohttp


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://google.com/') as resp:
            print(resp.status)
            print(await resp.text())

asyncio.run(main())