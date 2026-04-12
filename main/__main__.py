from main import Serena

import pyrogram
import asyncio
import logging


async def client():
      await Serena.start()
      await pyrogram.idle()
        

if __name__ == "__main__":
     logging.info('Bot Started!')
     Serena.loop.run_until_complete(client())
