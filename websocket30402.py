#ref: https://gist.github.com/rich20bb/4190781
#
# Set COMM Port (see: ser.port)
#
# Usage:
# [Anaconda2] C:\Users\cruncher>python websocket30402.py

import time
import struct
import socket
import hashlib
import base64
import sys
from select import select
import re
import logging
from threading import Thread
import signal

#---serial port comms.
# ref: http://pyserial.readthedocs.io/en/latest/index.html
import serial
import binascii

ser = serial.Serial()
ser.port = 'COM3' # tracker = 'COM10', rob3 = 'COM3'
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS # Data bits
ser.parity = serial.PARITY_NONE # Parity
ser.stopbits = serial.STOPBITS_ONE # Stop bits
ser.timeout = 1.0
ser.xonxoff = False # Software flow control.
ser.rtscts = False # Hardware flow control (RTS/CTS).
ser.srdtr = False # Hardware flow control (DSR/DTR).
ser.write_timeout = 1.0
ser.inter_byte_time = 1.0

try:
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()
#---serial port comms.

# Simple WebSocket server implementation. Handshakes with the client then echos back everything
# that is received. Has no dependencies (doesn't require Twisted etc) and works with the RFC6455
# version of WebSockets. Tested with FireFox 16, though should work with the latest versions of
# IE, Chrome etc.
#
# rich20b@gmail.com
# Adapted from https://gist.github.com/512987 with various functions stolen from other sites, see
# below for full details.

# Constants
MAGICGUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
TEXT = 0x01
BINARY = 0x02


# WebSocket implementation
class WebSocket(object):

    handshake = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Accept: %(acceptstring)s\r\n"
        "Server: TestTest\r\n"
        "Access-Control-Allow-Origin: http://localhost\r\n"
        "Access-Control-Allow-Credentials: true\r\n"
        "\r\n"
    )


    # Constructor
    def __init__(self, client, server):
        self.client = client
        self.server = server
        self.handshaken = False
        self.header = ""
        self.data = ""


    # Serve this client
    def feed(self, data):
    
        # If we haven't handshaken yet
        if not self.handshaken:
            logging.debug("No handshake yet")
            self.header += data
            if self.header.find('\r\n\r\n') != -1:
                parts = self.header.split('\r\n\r\n', 1)
                self.header = parts[0]
                if self.dohandshake(self.header, parts[1]):
                    logging.info("Handshake successful")
                    self.handshaken = True

        # We have handshaken
        else:
            logging.debug("Handshake is complete")
            
            # Decode the data that we received according to section 5 of RFC6455
            recv = self.decodeCharArray(data)
            
            #---serial port comms.
            if ser.isOpen():
                try:
                    ser.flushInput()    #flush input buffer, discarding all its contents
                    ser.flushOutput()   #flush output buffer, aborting current output
                                        #and discard all that is in buffer
                    #write data
                    #packet = "\xFF\xFF\x07\xFD\x19\xE2\x1C"
                    print recv
                    packet = ''.join(recv).decode('utf-8').encode('utf-16be') #IMPORTANT: 'strip()' removed. 'strip()' will remove 0x20 (white space).
                    #''.join(recv).strip().decode('utf-8')
                    #u'\xff\xff\x07\xfd\x19\xe2\x1c' (unicode)
                    print("Packet sent: " + '0x' + binascii.hexlify(packet))
                    packet = packet[1::2] # Drop every other, as they are 0x00
                    print("Packet sent: " + '0x' + binascii.hexlify(packet))
                    ser.write(packet)
                    time.sleep(0.5)  #give the serial port sometime to receive the data
                    numOfLines = 0
                    #recv = ['\xc3', '\xbf', '\xc3', '\xbf', '\x07', '\xc3', '\xbd', '\x19', '\xc3', '\xa2', '\x1c'] #ASCII from Unicode ('\xc3', '\xbf' = '\x00ff')
                    #recv = ['\xff', '\xff', '\x09', '\xfd', '\x59', '\xac', '\x52', '\x00', '\x00']
                    #recv = [u'\xff', u'\xff', u'\x09', u'\xfd', u'\x59', u'\xac', u'\x52', u'\x00', u'\x00']
                    #recv = ['\x00ff', '\x00ff', '\x0009', '\x00fd', '\x0059', '\x00ac', '\x0052', '\x0000', '\x0000']
                    #recv = ['\x00', '\xff', '\x00', '\xff', '\x00', '\x09', '\x00', '\xfd', '\x00', '\x59', '\x00', '\xac', '\x00', '\x52', '\x00', '\x00', '\x00', '\x00']
                    #recv = u""
                    recv = [] #Clean.
                    packetSize = 1 #MIN_PACKET_SIZE
                    while True:
                        numOfLines = numOfLines + 1
                        response = ser.read(1) # Blocking.
                        print("read data: " + '0x' + binascii.hexlify(response)) #Write hexadecimal to console.
                        recv.append(response.decode('latin1')) #'latin1' maps bytes 0-255 to unicode characters 0-255.
                        if(numOfLines >= packetSize): break
                        #recv = ['\xff', '\xff', '\x09', '\xfd', '\x59', '\xac', '\x52', '\x00', '\x00']
                except Exception, e1:
                    print "error communicating...: " + str(e1)
            else:
                print "cannot open serial port "
            #---serial port comms.
            
            # Send our reply
            ####for hex in recv: print '%x' % ord(hex[0])
            #self.sendMessage(''.join(recv).strip())
            self.sendMessage(''.join(recv).encode("utf8")) #''.join(recv).encode("utf8") IMPORTANT: removed '.strip()'.


    # Stolen from http://www.cs.rpi.edu/~goldsd/docs/spring2012-csci4220/websocket-py.txt
    def sendMessage(self, s):
        """
        Encode and send a WebSocket message
        """

        # Empty message to start with
        message = ""
        
        # always send an entire message as one frame (fin)
        b1 = 0x80

        # in Python 2, strs are bytes and unicodes are strings
        if type(s) == unicode:
            b1 |= TEXT
            payload = s.encode("UTF8")
            
        elif type(s) == str:
            b1 |= TEXT
            payload = s

        # Append 'FIN' flag to the message
        message += chr(b1)

        # never mask frames from the server to the client
        b2 = 0
        
        # How long is our payload?
        length = len(payload)
        if length < 126:
            b2 |= length
            message += chr(b2)
        
        elif length < (2 ** 16) - 1:
            b2 |= 126
            message += chr(b2)
            l = struct.pack(">H", length)
            message += l
        
        else:
            l = struct.pack(">Q", length)
            b2 |= 127
            message += chr(b2)
            message += l

        # Append payload to message
        message += payload

        # Send to the client
        self.client.send(str(message))


    # Stolen from http://stackoverflow.com/questions/8125507/how-can-i-send-and-receive-websocket-messages-on-the-server-side
    def decodeCharArray(self, stringStreamIn):
    
        # Turn string values into opererable numeric byte values
        byteArray = [ord(character) for character in stringStreamIn]
        datalength = byteArray[1] & 127
        indexFirstMask = 2

        if datalength == 126:
            indexFirstMask = 4
        elif datalength == 127:
            indexFirstMask = 10

        # Extract masks
        masks = [m for m in byteArray[indexFirstMask : indexFirstMask+4]]
        indexFirstDataByte = indexFirstMask + 4
        
        # List of decoded characters
        decodedChars = []
        i = indexFirstDataByte
        j = 0
        
        # Loop through each byte that was received
        while i < len(byteArray):
        
            # Unmask this byte and add to the decoded buffer
            decodedChars.append( chr(byteArray[i] ^ masks[j % 4]) )
            i += 1
            j += 1

        # Return the decoded string
        return decodedChars


    # Handshake with this client
    def dohandshake(self, header, key=None):
    
        logging.debug("Begin handshake: %s" % header)
        
        # Get the handshake template
        handshake = self.handshake
        
        # Step through each header
        for line in header.split('\r\n')[1:]:
            name, value = line.split(': ', 1)
            
            # If this is the key
            if name.lower() == "sec-websocket-key":
            
                # Append the standard GUID and get digest
                combined = value + MAGICGUID
                response = base64.b64encode(hashlib.sha1(combined).digest())
                
                # Replace the placeholder in the handshake response
                handshake = handshake % { 'acceptstring' : response }

        logging.debug("Sending handshake %s" % handshake)
        self.client.send(handshake)
        return True

    def onmessage(self, data):
        #logging.info("Got message: %s" % data)
        self.send(data)

    def send(self, data):
        logging.info("Sent message: %s" % data)
        self.client.send("\x00%s\xff" % data)

    def close(self):
        self.client.close()


# WebSocket server implementation
class WebSocketServer(object):

    # Constructor
    def __init__(self, bind, port, cls):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((bind, port))
        self.bind = bind
        self.port = port
        self.cls = cls
        self.connections = {}
        self.listeners = [self.socket]

    # Listen for requests
    def listen(self, backlog=5):

        self.socket.listen(backlog)
        logging.info("Listening on %s" % self.port)

        # Keep serving requests
        self.running = True
        while self.running:
        
            # Find clients that need servicing
            rList, wList, xList = select(self.listeners, [], self.listeners, 1)
            for ready in rList:
                if ready == self.socket:
                    logging.debug("New client connection")
                    client, address = self.socket.accept()
                    fileno = client.fileno()
                    self.listeners.append(fileno)
                    self.connections[fileno] = self.cls(client, self)
                else:
                    logging.debug("Client ready for reading %s" % ready)
                    client = self.connections[ready].client
                    data = client.recv(4096) # Data from HTML client.
                    fileno = client.fileno()
                    if data:
                        self.connections[fileno].feed(data)
                    else:
                        logging.debug("Closing client %s" % ready)
                        self.connections[fileno].close()
                        del self.connections[fileno]
                        self.listeners.remove(ready)
            
            # Step though and delete broken connections
            for failed in xList:
                if failed == self.socket:
                    logging.error("Socket broke")
                    for fileno, conn in self.connections:
                        conn.close()
                    self.running = False
                    
            # Read serial port.

# Entry point
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    server = WebSocketServer("", 30402, WebSocket)
    server_thread = Thread(target=server.listen, args=[5])
    server_thread.start()

    # Add SIGINT handler for killing the threads
    def signal_handler(signal, frame):
        logging.info("Caught Ctrl+C, shutting down...")
        #---serial port comms.
        ser.close() # Close serial port.
        #---serial port comms.
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        time.sleep(100)

