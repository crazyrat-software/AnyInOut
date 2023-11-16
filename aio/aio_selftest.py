from aio_serialprotocol import AIOSerialProtocol


class AIOSelfTest:

    def __init__(self):
        print("AIO-SelfTest init:")

    def selfTest(self):
        c = AIOSerialProtocol()
        c.setPitch(1.00)
        c.setRoll(3.00)
        c.setHeading(13.05)
        c.setDepth(-314.0)
        print(("[*] Setting parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] PRDID: " + repr(c.generatePRDID())))
        c.loadPRDID(c.generatePRDID())
        print(("[-] Reading parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        c.setPitch(2.00)
        c.setRoll(4.00)
        c.setHeading(15.05)
        c.setDepth(-234.0)
        print(("[*] Setting parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] HCHDM: " + repr(c.generateHCHDM())))
        c.loadHCHDM(c.generateHCHDM())
        print(("[-] Reading parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        c.setPitch(5.00)
        c.setRoll(7.00)
        c.setHeading(5.05)
        c.setDepth(34.0)
        print(("[*] Setting parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] HEHDT: " + repr(c.generateHEHDT())))
        c.loadHEHDT(c.generateHEHDT())
        print(("[-] Reading parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        c.setPitch(2.00)
        c.setRoll(9.00)
        c.setHeading(45.4)
        c.setDepth(74.3)
        print(("[*] Setting parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] SONDEP: " + repr(c.generateSONDEP())))
        c.loadSONDEP(c.generateSONDEP())
        print(("[-] Reading parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        c.setPitch(3.00)
        c.setRoll(5.00)
        c.setHeading(8.05)
        c.setDepth(74.3)
        print(("[*] Setting parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] DBS: " + repr(c.generateDBS())))
        c.loadDBS(c.generateDBS())
        print(("[-] Reading parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        c.setPitch(3.00)
        c.setRoll(5.00)
        c.setHeading(8.05)
        c.setDepth(74.3)
        print(("[*] Setting parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] SDDPT: " + repr(c.generateSDDPT())))
        #c.loadSDDPT(c.generateSDDPT())
        print(("[-] Reading parameters: Pitch:" + str(c.getPitch()) +
            " Roll:" + str(c.getRoll()) +
            " Heading:" + str(c.getHeading()) +
            " Depth:" + str(c.getDepth())))

        print(("\n[*] UTC: " + repr(c.generateUTC())))
        print(("\n[*] GPZDA: " + repr(c.generateGPZDA())))
