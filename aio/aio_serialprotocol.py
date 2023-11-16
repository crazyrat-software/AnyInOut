import array
import time
import logging


class AIOSerialProtocol:
    """Serial data protocol class implementation"""
    def __init__(self):
        logging.debug("AIO SerialProtocol Init")
        self.serialString = ""
        self.pitch = 0.0
        self.roll = 0.0
        self.heading = 0.0
        self.depth = 0.0
        self.depth_err = 0.0  # wartosc ustawiana podczas bledu odczytu

    def calculateChecksum2(self, s):
        ret = '%02X' % (-(sum(ord(c) for c in s) % 256) & 0xFF)
        return ret

    def calculateChecksum(self, s):
        b = array.array('B')
        b.fromstring(s)
        cs = reduce(lambda x, y: x ^ y, b)
        return format(cs, '02X')

    def setDepth(self, depth):
        if not isinstance(depth, float):
            raise TypeError
        self.depth = depth
        logging.debug("AIO SerialProtocol: Depth=" + str(self.depth))
        return self.depth

    def getDepth(self):
        return format(self.depth, '2.1f')

    def setPitch(self, deg):
        if not isinstance(deg, float):
            raise TypeError
        if ((deg >= 0) and (deg <= 360)):
            self.pitch = deg
        else:
            logging.debug("AIO SerialProtocol: Pitch value out of range")
            self.pitch = 0
        logging.debug("AIO SerialProtocol: Pitch=" + str(self.pitch))
        return self.pitch

    def getPitch(self):
        return format(self.pitch, '2.1f')

    def setRoll(self, deg):
        if not isinstance(deg, float):
            raise TypeError
        if ((deg >= 0) and (deg <= 360)):
            self.roll = deg
        else:
            logging.debug("AIO SerialProtocol: Roll value out of range")
            self.roll = 0
        logging.debug("AIO SerialProtocol: Roll=" + str(self.roll))
        return self.roll

    def getRoll(self):
        return format(self.roll, '2.1f')

    def setHeading(self, deg):
        if not isinstance(deg, float):
            raise TypeError
        if ((deg >= 0) and (deg <= 360)):
            self.heading = deg
        else:
            logging.debug("AIO SerialProtocol: Heading value out of range")
            self.heading = 0
        logging.debug("AIO SerialProtocol: Heading=" + str(self.heading))
        return self.heading

    def getHeading(self):
        return format(self.heading, '2.1f')

    def generatePRDID(self):
        header = "$PRDID"
        sep = ","
        footer = "\r\n"
        pitch = self.getPitch()
        roll = self.getRoll()
        heading = self.getHeading()
        msg = str(pitch) + sep + str(roll) + sep + str(heading)
        checksum = '*' + self.calculateChecksum("PRDID" + sep + msg)
        return header + sep + msg + checksum + footer

    def generateHCHDM(self):
        header = "$HCHDM"
        sep = ","
        footer = "\r\n"
        heading = self.getHeading()
        msg = str(heading) + sep + 'M'
        checksum = '*' + self.calculateChecksum("HCHDM" + sep + msg)
        return header + sep + msg + checksum + footer

    def generateHEHDT(self):
        header = "$HEHDT"
        sep = ","
        footer = "\r\n"
        heading = self.getHeading()
        msg = str(heading) + sep + 'T'
        checksum = '*' + self.calculateChecksum("HEHDT" + sep + msg)
        return header + sep + msg + checksum + footer

    def generateSONDEP(self):
        header = "$SONDEP"
        sep = ","
        footer = "\r\n"
        depth = self.getDepth()
        msg = str(depth) + sep + '1.1' + sep + 'M'
        checksum = '*' + self.calculateChecksum("SONDEP" + sep + msg)
        return header + sep + msg + checksum + footer

    def generateDBS(self):
        header = "$DBS"
        sep = ","
        footer = "\r\n"
        depth = self.getDepth()
        msg = str(depth) + sep + 'M'
        checksum = '*' + self.calculateChecksum("DBS" + sep + msg)
        return header + sep + msg + checksum + footer

    def generateGPZDA(self):
        header = "$GPZDA"
        sep = ","
        msg = time.strftime("%H%M%S.00,%d,%m,%Y,00,00")
        checksum = '*' + self.calculateChecksum("GPZDA" + sep + msg)
        footer = "\r\n"
        return header + sep + msg + checksum + footer

    def generateUTC(self):
        header = "000"
        sep = ","
        msg = time.strftime("%Y,%b,%d,%H%M%S") + ".00"
        footer = "\r\n"
        return header + sep + msg.upper() + footer

    def generateSDDPT(self):
        header = "$SDDPT"
        sep = ","
        footer = "\r\n"
        depth = self.getDepth()
        msg = str(depth) + sep + '0.0' + sep + "0.0"
        checksum = '*' + self.calculateChecksum("SDDPT" + sep + msg)
        return header + sep + msg + checksum + footer

    def loadPRDID(self, prdid):
        li = prdid.split(",")
        if (li[0] == "$PRDID"):
            pitch = float(li[1])
            if (isinstance(pitch, float)):
                self.setPitch(pitch)
            else:
                logging.error("AIO SerialProtocol: loadPRDID bad Pitch value '" + pitch + "'")
                self.setPitch(self.pitch_err)
            roll = float(li[1])
            if (isinstance(roll, float)):
                self.setRoll(roll)
            else:
                logging.error("AIO SerialProtocol: loadPRDID bad Roll value '" + roll + "'")
                self.setRoll(self.roll_err)
            heading = float(li[1])
            if (isinstance(heading, float)):
                self.setHeading(heading)
            else:
                logging.error("AIO SerialProtocol: loadPRDID bad Heading value '" + heading + "'")
                self.setHeading(self.heading_err)
        else:
            logging.error("AIO SerialProtocol: loadPRDID bad prefix '" + li[0] + "'")

    def loadHCHDM(self, hchdm):
        li = hchdm.split(",")
        if (li[0] == "$HCHDM"):
            heading = float(li[1])
            if (isinstance(heading, float)):
                self.setHeading(heading)
            else:
                logging.error("AIO SerialProtocol: loadHCHDM bad Heading value '" + heading + "'")
                self.setHeading(self.heading_err)
        else:
            logging.error("AIO SerialProtocol: loadHCHDM bad prefix '" + li[0] + "'")

    def loadHEHDT(self, hehdt):
        li = hehdt.split(",")
        if (li[0] == "$HEHDT"):
            heading = float(li[1])
            if (isinstance(heading, float)):
                self.setHeading(heading)
            else:
                logging.error("AIO SerialProtocol: loadHEHDT bad Heading value '" + heading + "'")
                self.setHeading(self.heading_err)
        else:
            logging.error("AIO SerialProtocol: loadHEHDT bad prefix '" + li[0] + "'")

    def loadSONDEP(self, sondep):
        li = sondep.split(",")
        if (li[0] == "$SONDEP"):
            depth = float(li[1])
            if (isinstance(depth, float)):
                self.setDepth(depth)
            else:
                logging.error("AIO SerialProtocol: loadSONDEP bad Depth value '" + depth + "'")
                self.setDepth(self.depth_err)
        else:
            logging.error("AIO SerialProtocol: loadSONDEP bad prefix '" + li[0] + "'")

    def loadDBS(self, dbs):
        li = dbs.split(",")
        if (li[0] == "$DBS"):
            depth = float(li[1])
            if (isinstance(depth, float)):
                self.setDepth(depth)
            else:
                logging.error("AIO SerialProtocol: loadDBS bad Depth value '" + depth + "'")
                self.setDepth(self.depth_err)
        else:
            logging.error("AIO SerialProtocol: loadDBS bad prefix '" + li[0] + "'")

    def getSerialString(self):
        return self.serialString

