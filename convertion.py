
from datetime import datetime

import logging

logging.basicConfig(filename='RNGLog.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

#convert Byte to integer
def convertIntFromBytes(digest):
    try:
        return int.from_bytes(digest, byteorder='big')
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

#Convert bytes to hexadecimal
def convertBytesToHex(digest):
    try:
        return ''.join(["%02X" % ord(x) for x in list(digest)[0]]).strip()
        #return ''.join(["%02X" % x for x in digest[0]]).strip()
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)

#Convert to hour, day, month, year
def parseHourDayMonthYear(blockTime):
    try:
        date_time = datetime.strptime(blockTime, '%Y-%m-%d %H:%M:%S')
        hour = date_time.time().hour
        day = date_time.date().day
        month = date_time.date().month
        year = date_time.date().year
        return hour, day, month, year
    except Exception as e:
        logging.error("Exception occured: ", exc_info=True)