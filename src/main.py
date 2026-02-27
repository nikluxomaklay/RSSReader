import asyncio
import os
from dotenv import load_dotenv


class Config:

    def __init__(self):
        if os.path.exists(".env"):
            load_dotenv(".env")


async def main():


    while True:
        ...

if __name__ == "__main__":
    asyncio.run(main())
