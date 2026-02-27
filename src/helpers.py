import os

import aiohttp
from dotenv import load_dotenv


def load_env():
    if os.path.exists(".env"):
        load_dotenv(".env")


async def io_get(url) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                return await response.text()
            except UnicodeDecodeError as ex:
                raw_bytes = ex.object
                if b'encoding="' in raw_bytes:
                    encoding = raw_bytes.split(
                        b'encoding="',
                    )[-1].split(b'"')[0]
                    return await response.text(encoding=encoding.decode())
                print(ex)
                return ''
