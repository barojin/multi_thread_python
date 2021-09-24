# Multi-thread practice
- ThreadPractice.py contains the code implementing threading examples to understand the use of threading library in python.<br>
- Referred to https://docs.python.org/3/library/threading.html <br>
- ThreadTutorial.py is the example in https://realpython.com/intro-to-python-threading/  
- PythonConcurrency.py in https://realpython.com/python-concurrency/  
- Async-IO-Python.py in https://realpython.com/async-io-python/  

## Keywords
- 

Reference: https://docs.python.org/3/library/threading.html

## Keywords in ThreadTutorial.py
- threading.Thread(target=function, args=(1, ))
- threading.Thread(target=function, args=(1, ), daemon=True)
- start()
- join()
- ThreadPoolExecutor in concurrent.futures (as of Python 3.2).
- Race Conditions so need to be synchronized for shared resources  
so we use threading.Lock or RLock

- ThreadPoolExecutor.submit(function, *args, **kwargs) that Set Threads and start them
- threading.Lock()
- Deadlock comes when you use the lock! So RLock come in for Deadlock

- RLock that allows a thread to .acquire() an RLock multiple times and    
call .release() the same number of times it called .acquire()

Producers consumers problem
threading.Event()

Queue is thread-safe.
Reference: https://realpython.com/intro-to-python-threading/