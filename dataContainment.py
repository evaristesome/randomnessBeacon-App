
import sqlite3
from sqlite3 import Error
from convertion import parseHourDayMonthYear
con = sqlite3.connect('randomnessBeacon.db')

hourBeacon =0
dayBeacon = 0
monthBeacon = 0
yearBeacon = 0

class data:

    # Create table
    def sqlTable(self):
        objectCursor = con.cursor()
        # need to rethink on the table structure: pulseDay integer, pulseMonth integer,pulseYear integer
        objectCursor.execute("""CREATE TABLE IF NOT EXISTS beaconsDB 
                            (ID integer PRIMARY KEY AUTOINCREMENT, 
                            currentTimeCur text, 
                            hashPrev text, 
                            beaconH text,
                            beaconD text,
                            beaconM text,
                            beaconY text,
                            hashCur text,  
                            precommitment text)""")
        con.commit()

    # insert data into the database
    def insertBeaconsinfo(self,entities):
        objectCursor = con.cursor()
        objectCursor.execute(
            '''INSERT INTO beaconsDB(currentTimeCur, hashPrev, beaconH, beaconD, beaconM, beaconY, hashCur, precommitment) VALUES(?,?,?,?,?,?,?,?)''', entities)
        # entities contain the different field to be inserted
        con.commit()

    def collectData(self, queueS1, queueS2):
        n=1
        # constantH, beaconH, constantD, beaconD, constantM, beaconM, constantY, beaconY
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

                if n==1:
                    precommitmentPrev = queueS1.get()
                    hashPrev = queueS1.get()
                    currentTimePrev = queueS1.get()
                    queueS1.empty()
                    n=n+1
                if n==2:
                    precommitmentCur = queueS1.get()
                    hashCur = queueS1.get()
                    currentTimeCur = queueS1.get()
                    queueS1.empty()
                    n = n + 1
                if n==3:
                    precommitment = queueS1.get()
                    hashNext = queueS1.get()
                    currentTimeNext = queueS1.get()
                    queueS1.empty()
                    n=n+1
                if n==4:
                    hourT, dayT, monthT, yearT = parseHourDayMonthYear(currentTimeCur)

                    if hourT != constantH:
                        beaconH = hashCur
                        constantH =hourT

                    if dayT != constantD:
                        beaconD = hashCur
                        constantD = dayT

                    if monthT != constantM:
                        beaconM = hashCur
                        constantH =hourT

                    if yearT != constantY:
                        beaconY = hashCur
                        constantY = yearT

                    print('Time: ', currentTimeCur)
                    print('Previous beacon: ', hashPrev)
                    print('Hour:', beaconH)                 #not yet in DB
                    print('Day: ', beaconD)                 #not yet in DB
                    print('Month: ', beaconM)               #not yet in DB
                    print('Year: ', beaconY)                #not yet in DB
                    print('Current beacon: ', hashCur)
                    print('Precommitment: ', precommitment)
                    print('Signature: ')
                    print()

                    currentTimeCur = currentTimeNext
                    hashPrev = hashCur
                    hashCur = hashNext

                    precommitment = queueS1.get()
                    hashNext = queueS1.get()
                    currentTimeNext = queueS1.get()

                    self.sqlTable()
                    entities =(str(currentTimeCur), str(hashPrev), str(beaconH), str(beaconD), str(beaconM), str(beaconY), str(hashCur), str(precommitment))
                    self.insertBeaconsinfo(entities)
#if __name__=='__main__':
    #objectContainment = dataContainment()