################################################################################
###
###@author: Jason Bensel
###@version: 457 Project 4
###Client server
###
################################################################################

import socket
import sys
import ast
import hashlib

class client(object):
    ############################################################################
    ###
    ### CLIENT CONSTRUCTOR
    ###
    ############################################################################
    def __init__(self, ipaddress, port):
        self.ipaddress = ipaddress
        self.port = port
        self.previousSeqNum = 1
        self.receivedPackets = {}
        self.receivedPacketNumbers = []
        self.receivedSequenceNumbers = [False, False, False, False, False]
        self.filename = ''
        self.fileSize = 0
        self.packetSize = 0
        self.hasPacketLoss = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ipaddress, self.port)
    
    ############################################################################
    ###
    ### Helper method for requesting a new file. Sends the file name and listens
    ### for acknowledgement.
    ###
    ###@param packet
    ###
    ############################################################################
    def sendPacketAndListenForAcknowledgement(self, packet):
        try:
            self.client_socket.sendto(str(packet), self.server_address)
            bytes = self.client_socket.recvfrom(1024)
            data = ast.literal_eval(bytes[0])
        except socket.timeout as te:
            data = self.sendPacketAndListenForAcknowledgement(packet)
        return data     
            
    ##########################################################################  
    #
    # Requests a new filename from the user, if nothing is receieved we request
    # another file
    #
    ##########################################################################  
    def requestNewFileName(self):
        self.filename = raw_input('Enter a file name: ')
        self.client_socket.settimeout(2)
        try:
            packet = ({'data': self.filename})
            data = self.sendPacketAndListenForAcknowledgement(packet)
            
            if data['alert'] == 'FNF':
                print data['alert']
                self.requestNewFileName()
            else:
                self.fileSize = data['fsize']
                self.packetSize = data['psize']
                #self.expectedPackets = self.fileSize / self.packetSize
                self.beginPacketHandling()
        except socket.timeout as te:
            print 'No response from server'
            self.requestNewFileName()
        
    ############################################################################
    ###
    ### Breaks the apart the headers, checksum, and data for the incoming packet
    ###
    ###@param bytes
    ###
    ############################################################################
    def parsePacketData(self, bytes):
        packetData = ast.literal_eval(bytes)
        data = packetData['data']
        sequenceNumber = int(packetData['sNum'])
        packetNumber = int(packetData['pNum'])
        endOfFile = int(packetData['EOF'])
        receivedChecksum = packetData['checksum']
        dataLength = len(packetData)
        del packetData['checksum']
        calculatedChecksum = self.calculateCheckSum(packetData)
        return data, sequenceNumber, packetNumber, endOfFile, dataLength, receivedChecksum, calculatedChecksum
    
    ############################################################################
    ###
    ### Constructs and appends to a dictionary for every packet receieved
    ###
    ###@param data
    ###@param sequenceNumber
    ###@param packetNumber
    ###
    ############################################################################
    def buildFileFromPackets(self, data, sequenceNumber, packetNumber):
        if packetNumber not in self.receivedPackets:
            self.receivedPackets[packetNumber] = data
            self.receivedPacketNumbers.append(packetNumber)
     
    ############################################################################
    ###
    ### Sends acknowledgements to server after every packet receieved
    ###
    ###@param sequenceNumber
    ###@param packetNumber
    ###
    ############################################################################
    def constructAndSendAcknowledgementPacket(self, sequenceNumber, packetNumber):
        packet = ({'sNum': sequenceNumber, 'pNum': packetNumber})
        self.client_socket.sendto(str(packet), self.server_address)
    
    ############################################################################
    ###
    ### Verifies end of file flag, writes file if receieved
    ###
    ###@param endOfFile
    ###@param packetNumber
    ###
    ############################################################################
    def checkFileFlagAndWriteFile(self, endOfFile, packetNumber):
        if endOfFile == 1:
            for x in range(int(packetNumber)):
                x += 1
                if(str(x) not in self.receivedPacketNumbers):
                    return False
            return True
    
    ############################################################################
    ###
    ### Calculates checksum of data
    ###
    ###@param packet
    ###
    ############################################################################
    def calculateCheckSum(self, packet):
        checksum = hashlib.md5(str(packet)).hexdigest()
        return checksum
   
    ############################################################################
    ###
    ### Writes file in order of the packet numbers
    ###
    ############################################################################
    def writeFile(self):
        file = open('writeFiles/'+self.filename, 'a+')
        for x in range(len(self.receivedPackets)):
            x += 1
            file.write(self.receivedPackets[x])
        file.close()
        self.client_socket.close()
        
    ############################################################################
    ###
    ### Handles receieving packets from server, order of packets on file save
    ### and timeout conditions
    ###
    ############################################################################
    def beginPacketHandling(self):
        while True:
            try:
                bytes, address = self.client_socket.recvfrom(1024)
                bytes = bytes.decode('utf-8')
                data, sequenceNumber, packetNumber, endOfFile, dataLength, receivedChecksum, calculatedChecksum = self.parsePacketData(bytes)
                print 'Receieved: ' + str(sequenceNumber)
                if receivedChecksum == calculatedChecksum:
                    self.buildFileFromPackets(data, sequenceNumber, packetNumber)
                    self.constructAndSendAcknowledgementPacket(sequenceNumber, packetNumber)
                    print endOfFile
                    print 'Sent Ack: ' + str(sequenceNumber)
                
                if endOfFile == 1:
                    self.writeFile()
                    break

            except socket.timeout as te:
                print 'packet not received'
                self.beginPacketHandling()
                


################################################################################
###
### Prompts user for ip address and port number, creates new instance of client
###
################################################################################
def main():
    #IPADDR = raw_input("Enter IP address: ")
    #PORT = raw_input("Enter PORT num: ")
    #PORT = int(PORT)
    
    #debugging convinience
    IPADDR = '127.0.0.1'
    PORT = 9876
    
    c = client(IPADDR, PORT)
    c.requestNewFileName()
    
main()