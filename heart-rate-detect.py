import os
import re
import time
import json

RESTING_HEART_RATE_RANGE = [40,100]
ERRATIC_HEART_RATE_RANGE = [100,160]

def getDataString():
    """
    Gets the current data string from the sensor.
    """
    os.environ["USBIP_SERVER"]='10.10.31.170'
    dev = usb.core.find(idVendor=0x0403, idProduct=0x6001) # Polar usb heart rate monitor
    if dev is None:
        raise ValueError('Device not found')

    # begin generic usb init
    dev.set_configuration()
	print usb.util.get_string(dev, 256, 1)
    print usb.util.get_string(dev, 256, 2)
    print usb.util.get_string(dev, 256, 3)
    # end generic usb init
	
	# begin ftdi init
    dev.ctrl_transfer(0x40,0x00,0,0,'')
    dev.ctrl_transfer(0x40,0x01,0,0,'')
    dev.ctrl_transfer(0x40,0x02,0,0,'')
    dev.ctrl_transfer(0x40,0x03,0x4138,0,'') # Set FTDI 9600 baudrate

    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]
    ep = intf[0]
    # end ftdi usb init

    while True:
        dev.write(0x02, 'G1\r') # send the read command to polar user monitor
        raw_data = dev.read(ep.bEndpointAddress, 0x40, intf, 0) # read the response message
        if raw_data is not None:
            string_data_array = raw_data.tostring().split(" ")
            if len(string_data_array) == 4: # check if the packet has valid format
                print "BPM: " + string_data_array[2]
                return raw_data.tostring()
        time.sleep(0.5)


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
    print "BPM threshold exceded!"
    pass


def main():
    jsonFile = open("edgepoint_feed_data.json")
    jsonData = json.load(jsonFile)

    # while data continues to be received
    for data in jsonData['heartrate_data']:
        currentHeartRate = data['bpm']
        time.sleep(1)

        if isErraticHeartRate(currentHeartRate):
            notifyDashboard()
        else:
            print currentHeartRate

    jsonFile.close()



if __name__ == '__main__':
    main()
