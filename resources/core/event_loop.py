import asyncio
import threading

# create a global event loop
loop = asyncio.new_event_loop()


# start the loop in a separate thread
def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()


threading.Thread(target=start_loop, daemon=True).start()
