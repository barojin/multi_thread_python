import logging
import threading
import time


def thread_function(name):
    logging.info(f"Thread {name}: starting")
    time.sleep(2)
    logging.info(f"Thread {name}: finishing")


def case1():
    this_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=this_format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Main: before creating thread")
    threads = []
    x = threading.Thread(target=thread_function, args=(1,), daemon=True)
    # when damone=True, the thread is terminated when __main__ reached the end.
    logging.info("Main: before running thread")
    x.start()
    logging.info("Main: wait for the thread to finish")
    x.join()  # let __main__ wait for x thread.
    logging.info("Main: all done!")


def case2():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = list()
    for index in range(3):
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=thread_function, args=(index,))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)


import concurrent.futures


def case3():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # ThreadPoolExecutor = context manager that automatically join()
    # The end of the with block causes the ThreadPoolExecutor to do a .join() \
    # on each of the threads in the pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(thread_function, range(3))
        # note: ThreadPoolExecutor will hide that exception without output


def put_format_logging_config():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


def case4():
    put_format_logging_config()

    db = FakeDatabase()
    logging.info(f"Testing update. Starting value is {db.value}.")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        [executor.submit(db.update, i) for i in range(2)]
    logging.info(f"Testing update. Ending value is {db.value}.")


class FakeDatabase:
    # make a race condition
    def __init__(self):
        self.value = 0 # shared data
        self._lock = threading.Lock()

    def update(self, name):
        logging.info(f"Thread {name}: starting update")
        local_copy = self.value
        local_copy += 1
        time.sleep(0.1)
        self.value = local_copy
        logging.info(f"Thread {name}: finishing update")

    def locked_update(self, name):
        logging.info(f"Thread {name}: starting update")
        logging.debug(f"Thread {name}: about to lock")
        # This ._lock is initialized in the unlocked state
        # and locked and released by the with statement.
        with self._lock:
            logging.debug(f"Thread {name}: has lock")
            local_copy = self.value
            local_copy += 1
            time.sleep(0.1)
            self.value = local_copy
            logging.debug(f"Thread {name}: about to release lock")
        """
        The below is the same code as above one
        self._lock.acquire()
        logging.debug(f"Thread {name}: has lock")
        local_copy = self.value
        local_copy += 1
        time.sleep(0.1)
        self.value = local_copy
        logging.debug(f"Thread {name}: about to release lock")
        self._lock.release()
        """
        logging.debug(f"Thread {name} after release")
        logging.info(f"Thread {name}: finishing update")


def case5():
    put_format_logging_config()
    logging.getLogger().setLevel(logging.DEBUG)
    db = FakeDatabase()
    logging.info(f"Testing update. Starting value is {db.value}.")
    n = 2
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        [executor.submit(db.locked_update, i) for i in range(n)]

    logging.info(f"Testing update. Ending value is {db.value}.")


class Pipeline:
    """
    class to allow a single element pipeline between producer and consumer
    """
    def __init__(self):
        self.message = 0
        self.producer_lock = threading.Lock()
        self.consumer_lock = threading.Lock()
        self.consumer_lock.acquire()

    def get_message(self, name):
        logging.debug(f"{name}:about to acquire consumer_lock")
        self.consumer_lock.acquire()
        logging.debug(f"{name}:have consumer_lock")
        msg = self.message
        logging.debug(f"{name}:about to release producer_lock")
        self.producer_lock.release()
        logging.debug(f"{name}:producer_lock released")
        return msg

    def set_message(self, message, name):
        logging.debug(f"{name}:about to acquire producer_lock")
        self.producer_lock.acquire()
        logging.debug(f"{name}:have producer_lock")
        self.message = message
        logging.debug(f"{name}:about to release consumer_lock")
        self.consumer_lock.release()
        logging.debug(f"{name}:consumer_lock released")


import random
SENTINEL = object()


def producer(pipeline):
    """Pretend we're getting a message from the network"""
    for index in range(10):
        message = random.randint(1, 101)
        logging.info(f"Producer set message: {message}")
        pipeline.set_message(message, "Producer")
    pipeline.set_message(SENTINEL, "Producer")


def consumer(pipeline):
    """Pretend we're saving a number in the database."""
    message = 0
    while message is not SENTINEL:
        message = pipeline.get_message("Consumer")
        if message is not SENTINEL:
            logging.info(f"Consumer get message: {message}")


def case6():
    """This case doesn't handle the burst of messages """
    put_format_logging_config()
    pipeline = Pipeline()
    # logging.getLogger().setLevel(logging.DEBUG)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer, pipeline)
        executor.submit(consumer, pipeline)


import queue


def producer_q(queue, event):
    while not event.is_set():
        data = random.randint(1, 10)
        logging.info(f"Producer put {data}")
        queue.put(data)
    logging.info("Producer exit.")


def consumer_q(queue, event):
    while not event.is_set() or not queue.empty():
        data = queue.get()
        logging.info(f"Consumer get {data} (size={queue.qsize()})")
    logging.info("Consumer exit.")


def case7():
    put_format_logging_config()

    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(producer_q, pipeline, event)
        executor.submit(consumer_q, pipeline, event)
  
        logging.info("Main: about to set event")
        event.set()


if __name__ == '__main__':
    # case1()
    # case2()
    # case3()
    # case4()
    # case5()
    # case6()
    case7()