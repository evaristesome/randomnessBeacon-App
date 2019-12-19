
import sqlite3
from convertion import parseHourDayMonthYear
con = sqlite3.connect('randomnessBeacon.db')

import logging
logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#logger=logging.getLogger(__name__)

class data:

    #sqlTable creates table structure if it does not exist
    def sqlTable(self):
        try:
            objectCursor = con.cursor()
            # need to rethink  the table structure: pulseDay integer, pulseMonth integer,pulseYear integer
            # to be inserted later: sourceRNG1 text, sourceRNG2 text, sourceHSM text, sourcePaul text
            objectCursor.execute("""CREATE TABLE IF NOT EXISTS beaconsDB 
                                (ID integer PRIMARY KEY AUTOINCREMENT, 
                                currentTimeCur text,    
                                sourceRNG1 text,
                                sourceRNG2 text,
                                sourceHSM text,
                                sourcePaul text,
                                outputValuePrev text, 
                                beaconH text,
                                beaconD text,
                                beaconM text,
                                beaconY text,
                                outputValueCur text,  
                                hashNext text)""")
            con.commit()
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    ''' 
    inserteaconsinfo function inserts data into the database
    '''
    def insertBeaconsinfo(self,entities):
        try:
            objectCursor = con.cursor()
            objectCursor.execute(
                '''INSERT INTO beaconsDB(currentTimeCur, sourceRNG1, sourceRNG2, sourceHSM, sourcePaul, outputValuePrev, beaconH, beaconD, beaconM, beaconY, outputValueCur, hashNext) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', entities)
            #to be inserted later: sourceRNG1, sourceRNG2, sourceHSM, sourcePaul,
            # entities contain the different field to be inserted
            con.commit()
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

    '''
    collectData function dequeues data from beaconEngine4 beaconEngineProcess/engine, displays and stores them in the database.
    The first time data are received, n = 1, they are buffered in containers with the extension Prev, i.e. previous.
    The second time data are received, n = 2, they are buffered in containers with the extension Cur, i.e. current.
    The third time data are received, n = 3, they are buffered in containers with the extension Next.
    After the first three rounds, everything plays out in n = 4:
        First: we display all buffered Prev, Cur, and Next. Pushing data to database happens in this phase
        Second: we buffer all Cur variables to Prev, Nexts to Curs, and dequeueing the queue to Nexts
        Third: we go back to First
    '''
    def collectData(self, queueS1, queueS2):
        try:
            n=1     # This constant serves for testing purpose to buffer data in previous, current, and next variables.
            # These constants serve for testing purpose of the hour, day, month, and year
            constantH = 60
            beaconH = 60
            constantD = 60
            beaconD = 60
            constantM = 60
            beaconM = 60
            constantY = 60
            beaconY = 60
            while True:
                while not queueS1.empty():

                    ''' 
                    These tests allow to keep data into variables, determine later what is previous, current or next.
                    '''
                    if n==1:
                        outputValuePrev = queueS1.get()     #precommitmentPrev = queueS1.get()   #
                        hashPrev = queueS1.get()            #
                        currentTimePrev = queueS1.get()     #
                        sourceRNG1 = queueS1.get()          #
                        sourceRNG2 = queueS1.get()          #
                        sourceHSM = queueS1.get()           #
                        sourcePaul = queueS1.get()
                        queueS1.empty()
                        n=n+1
                    if n==2:
                        outputValueCur = queueS1.get()      #precommitmentCur = queueS1.get()    #
                        hashCur = queueS1.get()             #
                        currentTimeCur = queueS1.get()      #
                        sourceRNG1 = queueS1.get()          #
                        sourceRNG2 = queueS1.get()          #
                        sourceHSM = queueS1.get()           #
                        sourcePaul = queueS1.get()
                        queueS1.empty()
                        n = n + 1
                    if n==3:
                        outputValueNext = queueS1.get()     #precommitment = queueS1.get()       #
                        hashNext = queueS1.get()            #
                        currentTimeNext = queueS1.get()     #
                        sourceRNG1Next = queueS1.get()          #
                        sourceRNG2Next = queueS1.get()          #
                        sourceHSMNext = queueS1.get()           #
                        sourcePaulNext = queueS1.get()
                        queueS1.empty()
                        n=n+1
                    if n==4:
                        hourT, dayT, monthT, yearT = parseHourDayMonthYear(currentTimeCur)

                        if hourT != constantH:
                            beaconH = outputValueCur       #     hashCur
                            constantH = hourT

                        if dayT != constantD:
                            beaconD = outputValueCur       #     hashCur
                            constantD = dayT

                        if monthT != constantM:
                            beaconM = outputValueCur       #     hashCur
                            constantM = monthT

                        if yearT != constantY:
                            beaconY = outputValueCur       #outputValueCur     hashCur
                            constantY = yearT

                        print('Time: ', currentTimeCur)
                        print('Source RNG_1: ', sourceRNG1)         #Additional
                        print('Source RNG_2:  ', sourceRNG2)        #Additional
                        print('Source RNG_HSM: ', sourceHSM)        #Additional
                        print('Source Paul RNG: ', sourcePaul)
                        print('Previous beacon: ', outputValuePrev)        #    hashPrev
                        print('Hour:', beaconH)
                        print('Day: ', beaconD)
                        print('Month: ', beaconM)
                        print('Year: ', beaconY)
                        print('Current beacon: ', outputValueCur)          #     hashCur
                        print('Precommitment: ', hashNext)     #        precommitment
                        print('Signature: ')
                        print()

                        currentTimeCur = currentTimeNext
                        outputValuePrev = outputValueCur      #        hashPrev = hashCur
                        outputValueCur = outputValueNext      #      hashCur = hashNext
                        sourceRNG1 = sourceRNG1Next
                        sourceRNG2 = sourceRNG2Next
                        sourceHSM = sourceHSMNext
                        sourcePaul = sourcePaulNext

                        outputValueNext = queueS1.get()       #outputValueNext
                        hashNext = queueS1.get()            #
                        currentTimeNext = queueS1.get()
                        sourceRNG1Next = queueS1.get()          #will add it to the dB lter
                        sourceRNG2Next = queueS1.get()          #will add it to the dB lter
                        sourceHSMNext = queueS1.get()           #will add it to the dB lter
                        sourcePaulNext = queueS1.get()           #will add it to the dB lter

                        self.sqlTable()
                        #entities =(str(currentTimeCur), str(outputValuePrev), str(beaconH), str(beaconD), str(beaconM), str(beaconY), str(outputValueCur), str(hashNext))
                        entities = (str(currentTimeCur), str(sourceRNG1), str(sourceRNG2), str(sourceHSM), str(sourcePaul), str(outputValuePrev), str(beaconH), str(beaconD), str(beaconM),str(beaconY), str(outputValueCur), str(hashNext))
                        self.insertBeaconsinfo(entities)
        except Exception as e:
            logging.error("Exception occured: ", exc_info=True)

#if __name__=='__main__':
    #objectContainment = dataContainment()