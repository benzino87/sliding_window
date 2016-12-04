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

class client(object):
    def __init__(self, ipaddress, port):
        self.ipaddress = ipaddress
        self.port = port
        self.previousSeqNum = 1
        self.receivedPackets = []
        self.data = []
        self.receivedSequenceNumbers = [False, False, False, False, False]
        self.filename = ''
        self.fileSize = 0
        self.packetSize = 0
        self.hasPacketLoss = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ipaddress, self.port)
    
    def sendPacketAndListenForAcknowledgement(self, packet):
        try:
            self.client_socket.sendto(str(packet), self.server_address)
            bytes = self.client_socket.recvfrom(1024)
            data = ast.literal_eval(bytes[0])
        except socket.timeout as te:
            data = self.sendPacketAndListenForAcknowledgement(packet)
        return data     
        
   
    def requestNewFileName(self):
        self.filename = raw_input('Enter a file name: ')
        self.client_socket.settimeout(2)
        packet = ({'data': self.filename})
        data = self.sendPacketAndListenForAcknowledgement(packet)
        
        if data['alert'] == 'FNF':
            print data['alert']
            self.requestNewFileName()
        else:
            self.fileSize = data['fsize']
            self.packetSize = data['psize']
            self.beginPacketHandling()
        
            
    def setDataArray(self):
        size = self.fileSize / self.packetSize
        print size
        for x in range(size):
            self.data.append('')
    
    def parsePacketData(self, bytes):
        packetData = ast.literal_eval(bytes)
        data = packetData['data']
        sequenceNumber = packetData['sNum']
        packetNumber = packetData['pNum']
        endOfFile = packetData['EOF']
        checksum = packetData['checksum']
        dataLength = len(packetData)
        print packetData
        return data, sequenceNumber, packetNumber, endOfFile, dataLength, checksum
    
    def buildFileFromPackets(self, data, sequenceNumber, packetNumber):
        self.receivedPackets.append(data)
        # self.receivedPackets[int(packetNumber)] = data
        #check if packet already exists 
        #check incoming packet vs larges packet
        # self.receivedSequenceNumbers[sequenceNumber-1] = True
        # self.receivedPackets.append(packetNumber)
        # self.data.append(data)
    
    def constructAndSendAcknowledgementPacket(self, sequenceNumber, packetNumber):
        packet = ({'sNum': sequenceNumber, 'pNum': packetNumber})
        self.client_socket.sendto(str(packet), self.server_address)
    
    def checkFileFlagAndWriteFile(self, endOfFile):
        if endOfFile == '1':
            self.writeFile()
            #self.client_socket.close()
    
    def writeFile(self):
        file = open('writeFiles/'+self.filename, 'a+')
        for data in self.receivedPackets:
            file.write(data)
        file.close()
    
    def beginPacketHandling(self):
        while True:
            bytes, address = self.client_socket.recvfrom(1024)
            bytes = bytes.decode('utf-8')
            data, sequenceNumber, packetNumber, endOfFile, dataLength, checksum = self.parsePacketData(bytes)
            self.buildFileFromPackets(data, sequenceNumber, packetNumber)
            self.constructAndSendAcknowledgementPacket(sequenceNumber, packetNumber)
            self.checkFileFlagAndWriteFile(endOfFile)
            if endOfFile == '1':
                break
                
                
                
                
                
                
                
            #     # self.writeFile(data, filename)
            #     if not self.checkForDuplicatePacket(packetNumber):
            #         ##check for ordered packets then construct file
            #         self.constructFileAndSetPacketNumbers(data, sequenceNumber, packetNumber)
                
            #     flagSuccessfullTransmission = ({'status': 1, 'sNum': sequenceNumber})

            #     self.client_socket.sendto(str(flagSuccessfullTransmission), self.server_address)
                
                
            #     if self.checkFileIntegrityWithEndFileFlag(endOfFile):
            #         break
                
                
            # except socket.timeout as packetError:
            #     failedSeqNumber = self.checkWindowPacketsIntegrity()
            #     flagFailedTransmission = ({'status': 0, 'sNum': sequenceNumber})
            #     self.client_socket.sendto(str(flagFailedTransmission), self.server_address)
            #     print "something went wrong" + packetError

            
        # try:
        #     self.receiveFileSize()
        #     # self.beginPacketHandling(self.filename)
        # except (Exception, socket.timeout) as e:
        #     self.requestNewFileName()
    
    
    
    # def receiveFileSize(self):
    #     try:
    #         self.client_socket.settimeout(2)
    #         bytes, address = self.client_socket.recvfrom(1024)
    #         packet = ast.literal_eval(bytes)
    #         self.fileSize = int(packet['fsize'])
    #         self.packetSize = int(packet['psize'])
    #         print self.fileSize
    #         print self.packetSize
    #     except socket.timeout as te:
    #         self.client_socket.sendto(self.filename, self.server_address)
    #         self.receiveFileSize()
            
        
    
 
        

    

    
    # def calculateCheckSum(self):
    #     return 0
    
    # def sendPacketAndListenForAcknowledgement(self, packet):
    #     try:
    #         self.client_socket.settimeout(2)
    #         self.client_socket.sendto(packet, self.server_address)
    #         self.client_socket.recvfrom(1024)
    #     except socket.timeout as te:
    #         data = self.sendPacketAndListenForAcknowledgement(packet)
    #         data = ast.literal_eval(data)
    #     return data
    # ############################################################################
    # ###
    # ###TODO check for all files
    # ###closes socket when file transfer is complete
    # ###@param: endOfFile
    # ###
    # ############################################################################

    
    # def checkWindowPacketsIntegrity(self):
    #     for i in range(5):
    #         if self.receivedPackets[i] == False:
    #             self.resetWindow()
    #             return i
    #     return -1
        
    # def resetWindow(self):
    #     for i in range(5):
    #         self.receivedPackets[i] = False
    
    # def checkForDuplicatePacket(self, packetNumber):
    #     if packetNumber in self.receivedPackets:
    #         return True
    #     return False
    
    # def checkForOutOfOrderPackets(self):
    #     return False
        



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