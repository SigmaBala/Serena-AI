from main import serena

import pyrogram
import asyncio
import logging


async def client():
      await serena.start()
      await pyrogram.idle()
        

if __name__ == "__main__":
     logging.info('Bot Started!')
     serena.loop.run_until_complete(client())
