from Queue import Queue
from threading import Thread, current_thread
 
def do_stuff(q):
  while True:
    s = current_thread().getName() + ":" + str(q.get())
    print s
    q.task_done()
 
q = Queue(maxsize=0)
num_threads = 10
 
for i in range(num_threads):
  worker = Thread(target=do_stuff, name="child"+str(i), args=(q,))
  worker.setDaemon(True)
  worker.start()
 
for x in range(100):
  q.put(x)
 
q.join()
 