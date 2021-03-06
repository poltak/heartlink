import os
import thread
import re
import time
import usb.core

RESTING_HEART_RATE_RANGE = [40,120]
ERRATIC_HEART_RATE_RANGE = [121,160]

STOP = [0,0]

GRIP_CLOSE = [1,0]
GRIP_OPEN = [2,0]
WRIST_UP = [4,0]
WRIST_DOWN = [8,0]
ELBOW_UP = [16,0]
ELBOW_DOWN = [32,0]
SHOULDER_UP = [64,0]
SHOULDER_DOWN= [128,0]

BASE_COUNTERCLOCKWISE = [0,1]
BASE_CLOCKWISE = [0,2]

duration = 1

arm = None
dev = None
ep = None
intf = None

def init_heartbeat_sensor():
    global dev, ep, intf
    os.environ["USBIP_SERVER"]='10.10.31.170'
    dev = usb.core.find(idVendor=0x0403, idProduct=0x6001) # Polar usb heart rate monitor
    if dev is None:
        raise ValueError('Heartbeat sensor not found')

    # begin generic usb init
    dev.set_configuration()
    # end generic usb init

    # begin ftdi init
    dev.ctrl_transfer(0x40,0x00,0,0,'')
    dev.ctrl_transfer(0x40,0x01,0,0,'')
    dev.ctrl_transfer(0x40,0x02,0,0,'')
    dev.ctrl_transfer(0x40,0x03,0x4138,0,'') #FTDI 9600 baudrate

    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]
    ep = intf[0]
    # end ftdi usb init

def init_robot_arm():
    global arm
    os.environ["USBIP_SERVER"]='10.10.31.170'
    arm = usb.core.find(idVendor=0x1267, idProduct=0)
    if arm is None:
        raise ValueError('Robot arm not found')

def robotArmCommand2(cmd, light):
    global arm
    c = list(cmd)
    c.append(light)
    arm.ctrl_transfer(0x40,6,0x100,0,c,1000)

def robotArmCommand(cmd, light, duration):
    global arm
    c = list(cmd)
    c.append(light)
    arm.ctrl_transfer(0x40,6,0x100,0,c,1000)
    time.sleep(duration)
    c = list(STOP)
    c.append(light)
    arm.ctrl_transfer(0x40,6,0x100,0,c,1000)

def robotArmLight(onoff):
    robotArmCommand2(STOP,onoff)

def robotArmGrip_close(onoff):
    global duration
    robotArmCommand(GRIP_CLOSE,onoff,duration)

def robotArmGrip_open(onoff):
    global duration
    robotArmCommand(GRIP_OPEN,onoff,duration)

def robotArmWrist(value, onoff):
    global duration
    if int(value)>0:
        robotArmCommand(WRIST_UP, onoff, duration)
    else:
        robotArmCommand(WRIST_DOWN, onoff, duration)

def robotArmElbow(value, onoff):
    global duration
    if int(value)<0:
        robotArmCommand(ELBOW_UP, onoff, duration)
    else:
        robotArmCommand(ELBOW_DOWN, onoff, duration)

def robotArmShoulder(value, onoff):
    global duration
    if int(value)>0:
        robotArmCommand(SHOULDER_UP, onoff, duration)
    else:
        robotArmCommand(SHOULDER_DOWN, onoff, duration)

def robotArmBase(value, onoff):
    global duration
    if int(value)>0:
        robotArmCommand(BASE_COUNTERCLOCKWISE,onoff, duration)
    elif int(value)<0:
        robotArmCommand(BASE_CLOCKWISE, onoff, duration)
    else:
        robotArmCommand2(STOP, 0)

def robotArmActionSeries():
	robotArmLight(1)
	time.sleep(2)
	robotArmLight(0)
	robotArmGrip_open(1)
	robotArmGrip_close(0)
	time.sleep(2)
	robotArmWrist(-1,1)
	robotArmWrist(1, 0)
	time.sleep(2)
	robotArmElbow(-1,1)
	robotArmElbow(1, 0)
	time.sleep(2)
	robotArmShoulder(-1,1)
	robotArmShoulder(1, 0)
	time.sleep(2)
	robotArmBase(-1,1)
	robotArmBase(1, 0)

def getDataString():
    """
    Gets the current data string from the sensor.
    """
    global dev, ep, intf
    while True:
        dev.write(0x02, 'G1\r') # send the read command to polar user monitor
        raw_data = dev.read(ep.bEndpointAddress, 0x40, intf, 0) # read the response message
        if raw_data is not None:
            string_data_array = raw_data.tostring().split(" ")
            if len(string_data_array) == 4: # check if the packet has valid format
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
    else:
        return False


def notifyDashboard():
    """
    Sends notifcation to be displayed on the dashboard user interface.
    TODO
    """
    print "BPM threshold exceded!"
    pass


def grumpyBot():
    try:
        robotArmLight(1)
        time.sleep(0.1)
        robotArmLight(0)
        time.sleep(0.1)
        robotArmLight(1)
        time.sleep(0.1)
        robotArmLight(0)
        time.sleep(0.1)
        robotArmLight(1)
        time.sleep(0.1)
        robotArmLight(0)
    except:
        print 'ignore'

def main():
    init_heartbeat_sensor()
    init_robot_arm()

    while True:
        currentHeartRate = parseDataString(getDataString())
        if isErraticHeartRate(int(currentHeartRate)):
            try:
                grumpyBot()
                thread.start_new_thread(notifyDashboard, ())
            except:
                print 'no start'

        # TODO: send BPM to server

        # DEBUG
        print "BPM: " + currentHeartRate


if __name__ == '__main__':
    main()
