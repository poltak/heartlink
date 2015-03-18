import usb.core
import time
 
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
 
def command2(cmd, light):
    c = list(cmd)
    c.append(light)
    dev.ctrl_transfer(0x40,6,0x100,0,c,1000)
 
def command(cmd, light, duration):
    c = list(cmd)
    c.append(light)
    dev.ctrl_transfer(0x40,6,0x100,0,c,1000)
    time.sleep(duration)
    c = list(STOP)
    c.append(light)
    dev.ctrl_transfer(0x40,6,0x100,0,c,1000)
 
def light(onoff):
    command2(STOP,onoff)
 
def grip_close(onoff):
    global duration
    command(GRIP_CLOSE,onoff,duration)
 
def grip_open(onoff):
    global duration
    command(GRIP_OPEN,onoff,duration)
 
def wrist(value, onoff):
    global duration
    if int(value)>0:
        command(WRIST_UP, onoff, duration)
    else:
        command(WRIST_DOWN, onoff, duration)
#         command2(STOP, 0)
 
def elbow(value, onoff):
    global duration
    if int(value)<0:
        command(ELBOW_UP, onoff, duration)
    else:
        command(ELBOW_DOWN, onoff, duration)
#         command2(STOP, 0)
 
def shoulder(value, onoff):
    global duration
    if int(value)>0:
        command(SHOULDER_UP, onoff, duration)
    else:
        command(SHOULDER_DOWN, onoff, duration)
#         command2(STOP, 0)
 
def base(value, onoff):
    global duration
    if int(value)>0:
        command(BASE_COUNTERCLOCKWISE,onoff, duration)
    elif int(value)<0:
        command(BASE_CLOCKWISE, onoff, duration)
    else:
        command2(STOP, 0)
 
light(1)
time.sleep(2)
light(0)
grip_open(1)
grip_close(0)
time.sleep(2)
wrist(-1,1)
wrist(1, 0)
time.sleep(2)
elbow(-1,1)
elbow(1, 0)
time.sleep(2)
shoulder(-1,1)
shoulder(1, 0)
time.sleep(2)
base(-1,1)
base(1, 0)