import re
import usb.core
import time

RESTING_HEART_RATE_RANGE = [40,100]
ERRATIC_HEART_RATE_RANGE = [100,160]

def getDataString():
    """
    Gets the current data string from the sensor.
    TODO
    """
    os.environ["USBIP_SERVER"]='10.10.31.170'
    dev = usb.core.find(idVendor=0x0403, idProduct=0x6001) # Polar usb heart rate monitor
    if dev is None:
        return ValueError('Device not found')

    # begin generic usb init
    dev.set_configuration()
    print usb.util.get_string(dev, 256, 1)
    print usb.util.get_string(dev, 256, 2)
    print usb.util.get_string(dev, 256, 3)
    # end generic usb init

    # begin ftdi init
    dev.ctrl_transfer(0x40, 0x3, 0x1a, 0x0)
    dev.ctrl_transfer(0x40, 0x1, 0x202, 0x0)
    dev.ctrl_transfer(0x40, 0x4, 0x8, 0x0)
    dev.ctrl_transfer(0x40, 0x2, 0x0, 0x0)
    dev.ctrl_transfer(0x40, 0x1, 0x100, 0x0)
    dev.ctrl_transfer(0x40, 0x6, 0x11a, 0x0)
    dev.write(2,'\r')
    # end ftdi init

    dev.write(2, 'G1\r')
    a = dev.read(1,64)
    print a.tostring()
    return a.tostring()
    time.sleep(5)
    #pass


def parseDataString(dataString):
    """
    Given an appropriately formatted data string from the sensor, extracts the
    relevant heart rate integer data, and returns it.

    Data string is formatted the following way:
    'STATUS TIMESTAMP BPM'
    all of which are integers
    """
    heartRateData = re.split(' ', dataString)
    heartRate = heartRateData[2]
    return heartRate


def isErraticHeartRate(heartRate):
    """
    Checks if current heart rate given is erratic, given the set threshold.
    """
    if ERRATIC_HEART_RATE_RANGE[0] <= heartRate <= ERRATIC_HEART_RATE_RANGE[1]:
        return True


def notifyDashboard():
    """
    Sends notifcation to be displayed on the dashboard user interface.
    TODO
    """
    pass



def main():
    # while data continues to be received
    while True:
        dataString = getDataString()
        currentHeartRate = parseDataString(dataString)

        if isErraticHeartRate(currentHeartRate):
            notifyDashboard()

def test():
    print 'before'
    print getDataString()
    print 'after'

if __name__ == '__main__':
    #main()
    test()
