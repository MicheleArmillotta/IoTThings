import threading
import time
import queue
import json
import socket
import struct

from service_discover.processor import process_tweet
from models.model import IoTContext

# Questa coda serve a comunicare col main
tweet_queue = queue.Queue()
address_queue = queue.Queue()
context = IoTContext()

class TweetListener(threading.Thread):
    def __init__(self, multicast_group='232.1.1.1', port=1235, buffer_size=1024):
        super().__init__(daemon=True)
        self.multicast_group = multicast_group
        self.port = port
        self.buffer_size = buffer_size
        self.running = True

        # Setup socket UDP multicast
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))  # riceve da tutte le interfacce

        local_ip = '192.168.8.237'
        mreq = struct.pack("4s4s", socket.inet_aton(self.multicast_group), socket.inet_aton(local_ip))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def run(self):
        print("[Listener] Starting tweet listener on multicast group...")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                tweet_json = data.decode('utf-8')
                print(f"[Listener] Received tweet from {addr}: {tweet_json}")
                tweet_data = json.loads(tweet_json)
                tweet_obj = process_tweet(tweet_data, context=context)
                if tweet_obj:
                    tweet_queue.put(tweet_obj)
                    address_queue.put(addr)
            except Exception as e:
                print(f"[Listener] Error while receiving or processing tweet: {e}")
            time.sleep(0.1)  # evita loop troppo aggressivo

    def stop(self):
        self.running = False
        self.sock.close()
