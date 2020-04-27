#Python multithreading example to print current date.
#1. Define a subclass using Thread class.
#2. Instantiate the subclass and trigger the thread. 

import threading
import datetime

class myThread (threading.Thread):
    def __init__(self, name, counter):
        threading.Thread.__init__(self)
        self.threadID = counter
        self.name = name
        self.counter = counter
    def run(self):
        print "\nStarting " + self.name
        print_date(self.name, self.counter)
        print "\nExiting " + self.name

def print_date(threadName, counter):
    datefields = []
    today = datetime.date.today()
    datefields.append(today)
    print "\n%s[%d]: %s" % ( threadName, counter, datefields[0] )

# Create new threads
thread1 = myThread("Thread_1", 1)
thread2 = myThread("Thread_2", 2)
thread3 = myThread("Thread_3", 3)
thread4 = myThread("Thread_4", 4)

# Start new Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()

print "\nCount thread before thread.join : %s" % ( threading.activeCount() )

thread1.join()
thread2.join()
thread3.join()
thread4.join()

print "\nCount thread :  %s" % ( threading.activeCount() )


print "Exiting the Program!!!"