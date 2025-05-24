# main.py
import threading
import queue
from gui.main_window import launch_gui
from service_discover.server import TweetListener, tweet_queue, address_queue
from service_discover.server import context
from service_discover.processor import process_tweet

if __name__ == "__main__":
    tweet_queue = queue.Queue()
    #context = IoTContext()

    # Start listener in background thread
    listener = TweetListener(multicast_group='232.1.1.1', port=1235)
    listener_thread = threading.Thread(target=listener.run, daemon=True)
    listener_thread.start()



    #TODO ===== > AGGIUSTARE LOGICA DI AGGIORNAMENTO DEL CONTESTO, DEVE FARLO processor.py PER FORZA 
    #TODO ===== > FARE TEST CON IL RASPBERRY



    # Launch GUI
    launch_gui(context)

