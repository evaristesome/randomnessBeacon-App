
from multiprocessing import Process, Queue
from beaconEngine4 import beaconEngineProcess
from dataContainment import data

#import threading

s1 = beaconEngineProcess()
s2 = data()

queueS1 = Queue()       #s1.engine() writes to queueS1

queueS2 = Queue()

s2 = Process(target=s2.collectData, args=(queueS1,queueS2))
s2.daemon = True
s2.start()
s1.engine(queueS1, queueS2)
s2.join()
#q = queue.Queue()
