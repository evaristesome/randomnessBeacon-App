
from multiprocessing import Process, Queue
from beaconEngine4 import beaconEngineProcess
from dataContainment import data

#import threading
import logging
logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#logger=logging.getLogger(__name__)

'''
This program allows to link two processes, to enqueue data: beaconEngine4 beaconEngineProcess/engine,
and to dequeue: dataContainment data/collectData
'''
try:
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
except Exception as e:
    logging.error("Exception occured: ", exc_info=True)
