import zmq
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)

class ZMQSubscriberModule:
    def __init__(self, context=None, max_workers=4):
        self.context = context or zmq.Context.instance()
        self.callbacks = {}  # Map: topic (bytes) -> callback_function
        self.running = False
        self.socket = None
        self.listener_thread = None
        
        # Initialize the thread pool
        # max_workers determines how many callbacks can run essentially "at once"
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def register_callback(self, topic_name, callback):
        """
        Register a callback for a specific topic.
        callback signature: func(topic, message)
        """
        # ZMQ topics must be bytes
        if isinstance(topic_name, str):
            topic_name = topic_name.encode('utf-8')
        
        self.callbacks[topic_name] = callback

    def start(self, connect_addr):
        """
        Start the single subscriber thread.
        """
        if self.running:
            log.debug("Subscriber already running, ignoring start()")
            return

        self.running = True
        log.info("Starting subscriber thread for %s", connect_addr)
        self.listener_thread = threading.Thread(
            target=self._subscribe_loop, 
            args=(connect_addr,),
            daemon=True
        )
        self.listener_thread.start()

    def stop(self):
        self.running = False
        log.info("Stopping subscriber module")
        
        # 1. Stop the listener thread
        if self.listener_thread:
            self.listener_thread.join()
            
        # 2. Shutdown the executor
        # wait=True ensures pending callbacks finish before we exit fully.
        # Set to False if you want to kill the module immediately.
        self.executor.shutdown(wait=True)

    def _subscribe_loop(self, connect_addr):
        """
        The main loop: Single socket, multiple topic filters.
        """
        # Create a new socket for this thread
        socket = self.context.socket(zmq.SUB)
        socket.connect(connect_addr)
        log.info("Connected SUB socket to %s", connect_addr)

        # Subscribe to all registered topics on ONE socket
        for topic in self.callbacks:
            socket.setsockopt(zmq.SUBSCRIBE, topic)
            log.debug("Subscribed to topic %s", topic)

        # Use a Poller to allow for non-blocking checks
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        while self.running:
            # Poll with timeout (100ms) to check self.running periodically
            socks = dict(poller.poll(100))

            if socket in socks and socks[socket] == zmq.POLLIN:
                try:
                    # Receive multipart: [topic, body]
                    topic, message = socket.recv_multipart()
                    
                    # Dispatch to the executor
                    if topic in self.callbacks:
                        callback_func = self.callbacks[topic]
                        
                        # SUBMIT the task to the pool.
                        # This is non-blocking; the loop immediately goes back 
                        # to waiting for the next ZMQ message.
                        self.executor.submit(
                            callback_func, 
                            topic.decode(), 
                            message
                        )
                
                except zmq.ZMQError as e:
                    log.exception("ZMQ error in subscribe loop: %s", e)

        # Cleanup socket when loop exits
        socket.close()
        log.info("Subscriber loop exited, socket closed")