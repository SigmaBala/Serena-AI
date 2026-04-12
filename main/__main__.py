from main import pbot

import pyrogram
import asyncio
import logging


async def client():
      await pbot.start()
      await pyrogram.idle()
        

if __name__ == "__main__":
     logging.info('Bot Started!')
     pbot.loop.run_until_complete(client())
