#!/usr/bin/env python


class accelerometer:
    #Basic imports
    import ctypes
    import sys
    #Phidget specific imports
    from Phidgets.Phidget import Phidget
    from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
    from Phidgets.Events.Events import AccelerationChangeEventArgs, AttachEventArgs, DetachEventArgs, ErrorEventArgs
    import Phidgets.Devices.Accelerometer

    def __init__(self):
        try:
            self.acc = Phidgets.Devices.Accelerometer.Accelerometer()
            self.acc.setOnAttachHandler(lambda e: self.onAttachHandler(e))
            self.acc.setOnDetachHandler(lambda e: self.onDetachHandler(e))
            self.acc.setOnErrorHandler(lambda e: self.onErrorHandler(e))
            self.acc.setOnAccelerationChangeHandler(lambda e: self.onAccelerationChangeHandler(e))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
        except RuntimeError as e:
            print("Runtime Exception: %s" % e.details)

        self.axis = [0.0, 0.0, 0.0]

    #Information Display Function
    def DisplayDeviceInfo(self):
        print("|------------|----------------------------------|--------------|------------|")
        print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
        print("|------------|----------------------------------|--------------|------------|")
        print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.acc.isAttached(), self.acc.getDeviceName(), self.acc.getSerialNum(), self.acc.getDeviceVersion()))
        print("|------------|----------------------------------|--------------|------------|")


    #Event Handler Callback Functions
    def onAttachHandler(self, e):
        attached = e.device
        print("Accelerometer %i Attached!" % (attached.getSerialNum()))
        n = accelerometer.getAxisCount()
        print("Number of Axes: %i" % (n))
        self.axis = [0.0] * n

        for i in range(n):
            accelerometer.setAccelChangeTrigger(n, 0.10)

    def onDetachHandler(self, e):
        detached = e.device
        print("Accelerometer %i Detached!" % (detached.getSerialNum()))

    def onErrorhandler(self, e):
        try:
            source = e.device
            print("Accelerometer %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

    def onAccelerationChangeHandler(self, e):
        source = e.device
        print("Accelerometer %i: Axis %i: %6f" % (source.getSerialNum(), e.index, e.acceleration))
        self.axis[e.index] = e.acceleration

    def someMain(self):
        #Main Program Code
        try:

        print("Opening phidget object....")

        try:
            self.acc.openPhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)

        print("Waiting for attach....")

        try:
            self.acc.waitForAttach(10000)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            try:
                self.acc.closePhidget()
            except PhidgetException as e:
                print("Phidget Exception %i: %s" % (e.code, e.details))
                print("Exiting....")
                exit(1)
            print("Exiting....")
            exit(1)
        
        try:
            numAxis = accelerometer.getAxisCount()
            accelerometer.setAccelChangeTrigger(0, 0.500)
            accelerometer.setAccelChangeTrigger(1, 0.500)
            if numAxis > 2:
                accelerometer.setAccelChangeTrigger(2, 0.500)
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
        
        self.DisplayDeviceInfo()

        print("Press Enter to quit....")

        chr = sys.stdin.read(1)

        print("Closing...")

        try:
            accelerometer.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Exiting....")
            exit(1)

        print("Done.")
        exit(0)


c = accelerometer()

c.someMain()
  