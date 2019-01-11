#!/usr/bin/evn python

import struct

class input_event():
    def __init__(self,sTime,sType,sCode,sValue):
        self.time = sTime
        self.Type = sType
        self.code = sCode
        self.value = sValue

class RawEventDataDecode():
    def __init__(self):
        self.EV_ABS = b'\x00\x03'
        self.EV_SYN = b'\x00\x00'

        self.SYNC_VALUE = b'\xff\xff\xff\xff'
        self.ABS_MT_POSITION_X = b'\x00\x35'
        self.ABS_MT_POSITION_Y = b'\x00\x36'

        #self.Y_START = 1580
        #self.Y_STEP = 210
        #self.X_STEP = 140
        
        self.Y_START = None
        self.Y_STEP = None
        self.X_STEP = None
        
        self.MAP_KEY = {
            0: ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            1: ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            2: ['shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '<-'],
            3: ['newMap', ',', 'emoji', ' ', ' ', ' ', ' ', '.', '\n']
        }
        
        self.readlength = None
        
        self.logPath = "CATCH_EVENTS"
        self.tpWidth = None
        self.tpHight = None
        self.lcdWidth = None
        self.lcdHight = None
        self.character = ""
        
    def startDecode(self):
        logFile = open(self.logPath,"rb")

        tmpRead = logFile.read(self.readlength)
        eventSet = []
        countEvent = 0

        while tmpRead != "":
            if len(tmpRead) != self.readlength:
                break

            (tmpTime,tmpType,tmpCode,tmpValue) = (tmpRead[self.readlength-9::-1],tmpRead[self.readlength-7:self.readlength-9:-1],tmpRead[self.readlength-5:self.readlength-7:-1],tmpRead[self.readlength-1:self.readlength-5:-1])

            if (tmpType == self.EV_SYN):
                countEvent = countEvent + 1
                eventSet.append(input_event(tmpTime, tmpType, tmpCode, struct.unpack('!L',tmpValue)[0]))
                #only process event set when ABS_SYN has came out twice which means there are two actions
                #They could be click,move or moving
                #   press + exit = click
                #   press + move = start move
                #   move + move = moving
                if (countEvent == 2):
                    self.character = self.character + self.eventSetProcess(eventSet)
                    eventSet = []
                    countEvent = 0
            elif (tmpType == self.EV_ABS):
                eventSet.append(input_event(tmpTime,tmpType,tmpCode,struct.unpack('!L',tmpValue)[0]))

            tmpRead = logFile.read(self.readlength)

        decodeChars = open("decodeLog","w+")
        decodeChars.write(self.character)
        decodeChars.close()
        return "Fine"

    def eventSetProcess(self,eventSet):
        if (len(eventSet) <= 5):
            return ""
        if (eventSet[-2].Type != self.EV_ABS and eventSet[-2].value != self.SYNC_VALUE):
            return ""
        else:
            touchX = None
            touchY = None
            for item in eventSet:
                if (item.code == self.ABS_MT_POSITION_X):
                    touchX = item.value*self.lcdWidth/(self.tpWidth+1)
                elif (item.code == self.ABS_MT_POSITION_Y):
                    touchY = item.value*self.lcdHight/(self.tpHight+1)

            if (touchX == None or touchY == None):
                return self.character[-1]

            yNum = int((touchY - self.Y_START)/self.Y_STEP)
            X_START = int(self.lcdWidth/10) if yNum == 0 else (int(self.lcdWidth/10) + int(self.lcdWidth/20))
            xNum = 0 if touchX < X_START else int((touchX - X_START)/int(self.lcdWidth/10))+1
            if (yNum > 3 or xNum > 10 or yNum < 0  or xNum < 0):
                return ""
            character = self.MAP_KEY[yNum][xNum]
            return character

    def start(self,width,height,arch):
        self.tpWidth = int(width)
        self.lcdWidth = int(width)
        self.tpHight = int(height)
        self.lcdHight = int(height)
        
        self.Y_START = int(self.lcdHight*0.65)
        self.Y_STEP = int((self.lcdHight - self.Y_START)/4)
        self.X_STEP = int(self.lcdWidth/10)
        self.readlength = 24 if "64" in arch else 16
        self.startDecode()

if __name__ == '__main__':
    RawEventDataDecode().start(720,1280,"arm64")