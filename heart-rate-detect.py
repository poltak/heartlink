import os
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
        raise ValueError('Device not found')

    # begin generic usb init
    dev.set_configuration()
    # end generic usb init

    dev.write(1, 'G1')
    return dev.read(1, 6)


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


def debug():
    print 'before'
    print getDataString()
    print 'after'


if __name__ == '__main__':
    #main()
    debug()
