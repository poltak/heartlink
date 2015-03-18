import usb.core
import time
import os

os.environ["USBIP_SERVER"]='10.10.31.170'
dev = usb.core.find(idVendor=0x1267, idProduct=0)
if dev is None:
    raise ValueError('Device not found')
 
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
 
def robotArmCommand2(cmd, light):
    c = list(cmd)
    c.append(light)
    dev.ctrl_transfer(0x40,6,0x100,0,c,1000)
 
def robotArmCommand(cmd, light, duration):
    c = list(cmd)
    c.append(light)
    dev.ctrl_transfer(0x40,6,0x100,0,c,1000)
    time.sleep(duration)
    c = list(STOP)
    c.append(light)
    dev.ctrl_transfer(0x40,6,0x100,0,c,1000)
 
def robotArmLight(onoff):
    command2(STOP,onoff)
 
def robotArmGrip_close(onoff):
    global duration
    command(GRIP_CLOSE,onoff,duration)
 
def robotArmGrip_open(onoff):
    global duration
    command(GRIP_OPEN,onoff,duration)
 
def robotArmWrist(value, onoff):
    global duration
    if int(value)>0:
        command(WRIST_UP, onoff, duration)
    else:
        command(WRIST_DOWN, onoff, duration)
#         command2(STOP, 0)
 
def robotArmElbow(value, onoff):
    global duration
    if int(value)<0:
        command(ELBOW_UP, onoff, duration)
    else:
        command(ELBOW_DOWN, onoff, duration)
#         command2(STOP, 0)
 
def robotArmShoulder(value, onoff):
    global duration
    if int(value)>0:
        command(SHOULDER_UP, onoff, duration)
    else:
        command(SHOULDER_DOWN, onoff, duration)
#         command2(STOP, 0)
 
def robotArmBase(value, onoff):
    global duration
    if int(value)>0:
        command(BASE_COUNTERCLOCKWISE,onoff, duration)
    elif int(value)<0:
        command(BASE_CLOCKWISE, onoff, duration)
    else:
        command2(STOP, 0)

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