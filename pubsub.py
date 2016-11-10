import eventlet
import time
import json
from eventlet import wsgi, websocket, event, greenpool

class Router:
   """ This class routes data around the place between publishers and subscribers
       Feeds are generic tuples or strings
   """
   def __init__(self):
       self.feeds_subs  = {} # maps feed keys to the events for subscribers
       self.feeds_e_sem = eventlet.semaphore.Semaphore()
       self.pool        = greenpool.GreenPool()
       self.feeds_sems  = {}

   def notify_waiters(self,waiters,k,v):
       with self.feeds_sems[k]:
          for r in self.pool.imap(lambda x: x.send(v), waiters):
              pass

   def publish(self,k,v):
       with self.feeds_e_sem:
          if not self.feeds_subs.has_key(k): return # if it doesn't exist, that means no subscribers, so don't waste the CPU time on it
          waiters = list(self.feeds_subs[k])
   
       self.pool.spawn_n(self.notify_waiters,waiters,k,v)

   def subscribe(self,k):
       my_e = event.Event()
       with self.feeds_e_sem:
          if not self.feeds_subs.has_key(k):
             self.feeds_subs[k] = set()
             self.feeds_sems[k] = eventlet.semaphore.Semaphore()
          self.feeds_subs[k].add(my_e)
       while True:
         yield my_e.wait()
         with self.feeds_e_sem:
            self.feeds_subs[k].remove(my_e)
            my_e = event.Event()
            self.feeds_subs[k].add(my_e)

