#!/usr/bin/env python

# GET http://localhost:5000

import os
import sys
import usb.core
import struct
import getopt

import threading, socket
# from sysconfig import *
from string import *
from select import *
from threading import Thread
import time
import traceback
import mimetools
from StringIO import StringIO

MSGLEN = 2048
app_version = "1.0"

# +++ customize these if needed
doublemint_MAC = '0022bdcf4894'
catalyst_switch_IP = '192.168.1.50'
webserver_host = '0.0.0.0'  # preferred way is to use dns or dotted-quads (ip addr)
#webserver_host = '192.168.1.11'
webserver_port = 5000
# --- (customize/end)

class DmoIf(threading.Thread):

     def __init__(self, port, callback=None):
          threading.Thread.__init__(self)
          self.port = port
          self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
          self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

          if port != None:
               self.sock.bind((webserver_host, self.port))
               self.sock.listen(5)
          else:
               raise RuntimeError('Port number required')

          if callback == None:
               raise RuntimeError('Message handler required')
          else:
               self.callback = callback

          self.shut = 0 

          # begin Doublemint initialization
          os.environ["USBIP_SERVER"] = catalyst_switch_IP
          self.dev = usb.core.find(address=int(doublemint_MAC, 16)) # find Doublemint using MAC address
          if self.dev is None:
               print "Doublemint not found (searching for MAC: [" + doublemint_MAC + "] and switch IP: [" + catalyst_switch_IP + "]"
               raise ValueError

          self.dev.set_configuration()

          #print usb.util.get_string(self.dev, 256, 1)
          #print usb.util.get_string(self.dev, 256, 2)
          #print usb.util.get_string(self.dev, 256, 3)

          # write 0's to the 2 digital outputs
          self.output0 = 0
          self.output1 = 0
          # end Doublemint initialization


     def send(self, sock, msg):
          if (type(msg) is str):
               hdr = "HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: {0}\r\n\r\n"
               hdr = hdr.format(len(msg))
               m = hdr + msg
               print "returning ascii json data '%s' to web client" % msg

          else:
               hdr = "HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream; charset=utf-8\r\nContent-Length: {0}\r\n\r\n"
               hdr = hdr.format(4) # force to long
               m = hdr + struct.pack('!L', msg)

          totalsent = 0
          while totalsent < len(m):
               sent = 0
               try:
                    sent = sock.send(m[totalsent:])
                    #if sent == 0:
                    #raise RuntimeError("socket connection broken")
               except socket.error, UnboundLocalError:
                    return

               totalsent = totalsent + sent
          sock.close()


     def receive (self, client, addr ):
          global MSGLEN

          chunks = [] 
          bytes_recd = 0
          client.settimeout(1)

          while bytes_recd < MSGLEN:
               try :
                    chunk = client.recv(min(MSGLEN- bytes_recd, MSGLEN))
               except socket.error, UnboundLocalError:
                    #print msg
                    break

               if not chunk : 
                    client.close()
                    break

               if chunk == '':
                    raise RuntimeError("socket connection broken")

               chunks.append(chunk)
               #print "received " + str(len(chunk)) + " bytes..."
               bytes_recd += len(chunk)

          hdr = ''.join(chunks)
          print 'hdr=[' + hdr + ']'

          # sanity check: if hdr is empty, don't try to extra data from the payload!
          if len(hdr) == 0:
               #print 'empty header found - ignoring this'
               chunks = [] 
               bytes_recd = 0
               return

          req, h = hdr.split('\r\n' , 1)
          m = mimetools.Message(StringIO(h))
          #m.dict['method'], m.dict['path'], m.dict['http-version'] = req.split()

          if len(req.split()) == 3:
                 m.dict['method'], m.dict['path'], m.dict['http-version'] = req.split()
                 #print "method=[%s] path=[%s] version=[%s]" % (m.dict['method'], m.dict['path'], m.dict['http-version'])
          else:
                 m.dict['path'] = '/'
                 m.dict['method'],  m.dict['http-version'] = req.split()
                 #print "method=[%s] path=[%s] version=[%s]" % (m.dict['method'], m.dict['path'], m.dict['http-version'])

          if m.dict['method'] == 'GET' :
               resp = self.callback(self, 0)
               self.send(client, resp)

          if m.dict['method'] == 'PUT' :
               query = m.dict['path'][2:].split('&')
               args = []
               #if len(args) > 0 :
               for q in query:
                    args.append(q.split('=')[1]);

               print "args0:"+args[0]
               print "args1:"+args[1]

               resp = self.callback(self, 1, args[0], args[1])
               self.send(client, resp)


     def start (self) :
          while 1:   
               #print 'waiting for connection...'
               client, addr = self.sock.accept()
               #print '...connected from:', addr
               Thread(self.receive(client,addr))


     def handler (self, method, port=None, value=None):
          #print "handler " + str(method) + str(port) + str(value)

          # do a READ from the sensor
          if (method == 0):
               data = self.dev.read(1, 53)
               analog0 = data[0x07] | ((data[0x06] & 0x0f) << 8)
               analog1 = data[0x05] | ((data[0x06] & 0xf0) << 4)

               # return ascii data (like the arduino)
               ret_json_data = '''{"ANALOG":{"Port0":%d,"Port1":%d}}''' % (analog0, analog1)
               #ret_json_data = '''\n{\n\t"ANALOG":\n\t{\n\t\t"Pressure":%d,\n\t\t"Light":%d\n\t}\n}\n''' % (analog0, analog1)
               return ret_json_data


          # do a WRITE to the sensor
          elif (method == 1):
               if (port == '0'):
                    print "doing a WRITE to port 0, value=[%d]" % int(value)
                    self.output0 = int(value)

               if (port == '1'):
                    print "doing a WRITE to port 1, value=[%d]" % int(value)
                    self.output1 = int(value)

               # I assume this does a write to either of the 2 digital out lines (leds) ?
               self.dev.ctrl_transfer(0x21, 0x9, 0x200, 0x0, 
                                      [(self.output1<<1) | (self.output0)<<0, 0x77, 0x01]) 
               return 0



if __name__ == "__main__":
     try:
	     opts, args = getopt.getopt(sys.argv[1:], "m:s:p:")
     except getopt.GetoptError as err:
          # print help information and exit:
	  print "usage: python_usb_sensors_webserver_ascii -m <doublemint_mac> -s <switch_ip> -p <http_port>"
	  sys.exit(2)

     for opt, arg in opts:
	  if opt == '-m':
               doublemint_MAC = arg
	  elif opt == '-s':
               catalyst_switch_IP = arg
	  elif opt == '-p':
               webserver_port = int(arg)

     print "python web-server for USB sensors, version [" + app_version + "], running on IP: [" + webserver_host + "], TCP port: [" + str(webserver_port) + "]"
     print " Connected to doublemint MAC: [" + doublemint_MAC + "] and switch IP: [" + catalyst_switch_IP + "]"
     print 

     d = DmoIf(port=webserver_port, callback=DmoIf.handler)
     d.start()

