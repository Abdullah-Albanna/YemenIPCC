from threading import Thread

def startThread(target, name, logging ,*args):
    try:
        Thread(target=target, args=args, daemon=True).start()
        logging.debug(f"Ran the {name} thread")
    except Exception as e:
        logging.error(f"An error occurred while running the {name} thread, error: {e}")