
from datetime import datetime

#convert Byte to integer
def convertIntFromBytes(digest):
    return int.from_bytes(digest, byteorder='big')

#Convert bytes to hexadecimal
def convertBytesToHex(digest):
    return ''.join(["%02X" % ord(x) for x in list(digest)[0]]).strip()
    #return ''.join(["%02X" % x for x in digest[0]]).strip()

#Convert to hour, day, month, year
def parseHourDayMonthYear(blockTime):
    date_time = datetime.strptime(blockTime, '%Y-%m-%d %H:%M:%S')
    hour = date_time.time().hour
    day = date_time.date().day
    month = date_time.date().month
    year = date_time.date().year
    return hour, day, month, year



