################################################################################
###
### @author: Jason Bensel
### @version: CIS 457 Project 4
### UDP Sliding window file transfer
###
################################################################################
import sys
import socket
import os
import struct
import threading
import ast

class server(object):
    def __init__(self, ipaddress, port):
        self.ipaddress = ipaddress
        self.port = port
        self.filename = ''
        self.fileSize = 0
        self.packetNumber = 1
        self.endOfFile = '0'
        self.receivedFailedPacket = False
        self.isFirstIteration = True
        self.startIndex = 0
        self.endIndex = 0
        self.dataSize = 0
        self.failedPacketNumber = 0
        self.failedSeqNumber = 0
        self.receivedPackets = []
        self.windowPackets = []
        self.acknowledgedSequenceNumber = [False, False, False, False, False]
        self.acknowledgedPackets = [0, 0, 0, 0, 0]
        self.client_address = ''
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ipaddress, self.port)
        self.server_socket.bind(self.server_address)
        print 'listening on: '+ self.ipaddress
    
    def sendPacketAndListenForAcknowledgement(self, packet):
        try:
            self.server_socket.sendto(str(packet), self.client_address)
            bytes = self.server_socket.recvfrom(1024)
            data = ast.literal_eval(bytes[0])
        except socket.timeout as te:
            data = self.sendPacketAndListenForAcknowledgement(packet)
        return data  
    

    ################################################################################
    ### Clears fields when incorrect file is loaded
    ### @param: filename
    ### @param: isFirstIteration
    ################################################################################
    def clearFileFields(self):
        self.filename = ''
        self.isFirstIteration = False
    
    ################################################################################
    ### Uses Indexes to load specific portions of the file
    ### @param: filename
    ### @param: start_index
    ### @param: end_index
    ### @param: isFileReadComplete
    ################################################################################
    def getPacketFromFile(self):
        try:
            if self.endIndex > self.fileSize:
                self.endIndex = self.fileSize
                self.endOfFile = '1'
            
            with open(self.filename) as fin:
                fin.seek(self.startIndex)
                data = fin.read(self.endIndex - self.startIndex)
    
        except IOError as e:
            print 'file request: ' + self.filename
            raise Exception
        
        return data
    
    ############################################################################
    ### Handles manipulating indexes, packet numbers and sequence numbers when   
    ### the server detects that the client did not receieve a package
    ### @param: sequenceNumber 
    ### @param: packetNumber
    ############################################################################
    def resetIndexesGivenFailedPacketResponse(self):
        self.packetNumber = self.failedPacketNumber
        self.startIndex = self.dataSize*self.failedPacketNumber
        self.endIndex = (self.dataSize*self.failedPacketNumber) + self.dataSize

    
    ############################################################################  
    ###
    ###Determines indexes for each file load
    ###
    ############################################################################
    def setIndexesForDataFetch(self):
        if  self.isFirstIteration:
            self.startIndex = 0
            self.endIndex = self.dataSize
            self.isFirstIteration = False
        else:
            self.startIndex += self.dataSize
            self.endIndex += self.dataSize
    
    def setDataSize(self, data):
        if '.txt' in data:
            self.dataSize = 900
        else:
            self.dataSize = 200

    ############################################################################  
    ###
    ###Checks to see if the file exists, sets the filename. otherwise notifies
    ###client that file does not exist
    ###@param: address
    ###@param: data
    ###
    ############################################################################    
    def checkFileNameIntegrity(self, data):
        try:
            self.fileSize = os.path.getsize(data)
            self.filename = data
            self.setDataSize(data)
            packet = ({'fsize': self.fileSize, 'psize': self.dataSize, 'alert': ''})
            return packet
        except OSError:
            packet = ({'alert': 'FNF'})
            return packet
    ############################################################################  
    ###
    ###Opens server socket to recieve initial file request from client
    ###
    ############################################################################           
    def listenForFileName(self):
        
        #Receive file request from client
        bytes, address = self.server_socket.recvfrom(1024)
        
        self.client_address = address
        
        data = ast.literal_eval(bytes)
        filename = data['data']
        print 'File Request: ' + filename

        packet = self.checkFileNameIntegrity(filename)
        
        if packet['alert'] == 'FNF':
            print 'File Not Found'
            self.server_socket.sendto(str(packet), self.client_address)
            self.listenForFileName()
        
        else:
            self.server_socket.sendto(str(packet), self.client_address)
            self.sendPackets()
            print 'success'
        
        
        # if self.checkFileNameIntegrity(address, data):
        #     self.sendFileSizePacket(address)
        #     # self.sendPackets(address)
        # ELSE:
        #     print 'File does not exist'
        #     self.listenForFileName()
    
    def sendFileSizePacket(self, address):
        packet = ({'fsize': self.fileSize, 'psize': self.dataSize})
        self.server_socket.sendto(str(packet), address)
        self.listenForAcknowledgement(address)
        
    def listenForAcknowledgement(self, address):
        try:
            self.server_socket.settimeout(2)
            data = self.server_socket.recvfrom(1024)
        except socket.timeout as te:
            self.sendFileSizePacket(address)
    
    def checkConfirmationPacket(self, sequenceNumber):
        data = self.server_socket.recvfrom(1024)
        self.server_socket.settimeout(2)
        if data == sequenceNumber:
            return True
        else:
            return False
    
    def calculateCheckSum(self):
        return 0
    
    def verifyResponsePacket(self, bytes):
        packetData = ast.literal_eval(bytes)
        if packetData['status'] == '0':
            self.failedSeqNumber = int(packetData['sNum'])
            sequenceNumber = self.resetIndexesGivenFailedPacketResponse()
            return sequenceNumber, 'Failed: ' + str(self.failedSeqNumber), True
        else:
            sequenceNumber = int(packetData['sNum'])
            return sequenceNumber, 'Received: ' + str(sequenceNumber), False
            
    def constructPackets(self):
        sequenceNumber = 1
        while sequenceNumber <= 5:
            self.setIndexesForDataFetch()
            data = self.getPacketFromFile()
            packet = ({'sNum': sequenceNumber, 'pNum': self.packetNumber, 
                        'data': data, 'EOF' : self.endOfFile, 'checksum': 0 })
            self.windowPackets.append(packet)
            sequenceNumber +=1
            self.packetNumber += 1
        self.sendPacketsInWindow(packet)
    
    def sendPacketsInWindow(self, packet):
        for packet in self.windowPackets:
            try:
                self.server_socket.sendto(str(packet), self.client_address)
                bytes = self.server_socket.recvfrom(1024)
                data = bytes[0]
                data = ast.literal_eval(data)
                self.acknowledgedSequenceNumber[int(data['sNum'])-1] = True
                self.acknowledgedPackets[int(data['sNum'])-1] = int(data['pNum'])
            except socket.timeout as st:
                continue
        self.windowPackets = []
            
    def checkResponsesAndAdjustWindow(self):
        for i in range(len(self.acknowledgedPackets)):
            if self.acknowledgedPackets[i] == False:
                self.failedPacketNumber = self.acknowledgedPackets[i-1] + 1
                break
            
        
        
                
    ##########################################################################  
    #
    #Method that handles sending packets within the sliding window
    #
    ########################################################################## 
    def sendPackets(self):
        while True:
            self.constructPackets()
            self.checkResponsesAndAdjustWindow()
            if self.endOfFile == '1':
                break
        
        
    #     # quenceNumber = 1
        
    #   wh# ile sequenceNumber <= 5:
    #     #   try:
    #     #       self.setIndexesForDataFetch()
    #     #       data = self.getPacketFromFile()
    #     #       packet = ({'sNum': sequenceNumber, 'pNum': self.packetNumber, 
    #     #                   'data': data, 'EOF' : self.endOfFile, 'checksum': 0 })
                
    
                            
    #           se# lf.server_socket.sendto(str(packet).encode('utf-8'), address)
    #           pr# int 'Sent: ' + str(packet['sNum'])
                
    #           re# sponse = self.server_socket.recvfrom(1024)
                
    #         #   sequenceNumber, result, receivedFailed = self.verifyResponsePacket(response[0])
    #         #   print result
                
                
    #         #   if receivedFailed == False:
    #         #       if self.endOfFile == '1':
    #         #           break
                    
    #         #       if sequenceNumber == 5:
    #         #           sequenceNumber = 1
    #         #           self.packetNumber += 1
    #         #       else:
    #         #           sequenceNumber += 1
    #         #           self.packetNumber += 1
            
    #       ex# cept socket.timeout:
    #         #   self.failedSeqNumber = sequenceNumber
    #         #   self.failedPacketNumber = self.packetNumber
    #         #   sequenceNumber = self.resetIndexesGivenFailedPacketResponse(self.failedPacketNumber)
            
def main():
    
    #IPADDR = raw_input("Enter IP address: ")
    #PORT = raw_input("Enter PORT num: ")
    #PORT = int(PORT)
    
    #debugging convinience
    IPADDR = '127.0.0.1'
    PORT = 9876
    
    s = server(IPADDR, PORT)
    s.listenForFileName()
    
main()




    





        


        
        
        
    # sequenceNumber = 1
    
    # while sequenceNumber <= 5:
        
        
    #     isFirstIteration, startIndex, endIndex = setIndexesForDataFetch(isFirstIteration, startIndex, endIndex)
        
    #     try:
    #         data, isFileReadComplete = getPackets(filename, startIndex, endIndex, isFileReadComplete)
    #     except Exception:
    #         server_socket.sendto('FNF', address)
    #         filename, isFirstIteration = clearFileFields(filename, isFirstIteration)
    #         break
        
    #     server_socket.settimeout(2)
        
    #     packet = ({'seq_num': sequenceNumber, 'packet_number': packetNumber, 'data': data})
        
    #     #debugging
    #     #print packet
        
    #     string_packet = str(packet)
        
    #     #print string_packet
        
    #     server_socket.sendto(string_packet, address)
    #     print 'Sent: ' + str(sequenceNumber)
        
    #     #Receive file request from client
    #     confirmation_data, address = server_socket.recvfrom(1024)
        
    #     print 'Confirmation: ' + confirmation_data
        
    #     #Check for packet failed notification
    #     if confirmation_data == 'failed':
    #         failedPacketNumber = packetNumber
    #         failedSeqNumber = sequenceNumber
    #         recievedFailedPacket = True
        
    #     receivedPackets.append(confirmation_data)
        
    #     sequenceNumber, packetNumber = checkFailedPacketResponse(sequenceNumber, packetNumber)
        
    #     if isFileReadComplete == True:
    #         break
        
# listenForFileName()


    