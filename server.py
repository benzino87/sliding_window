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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ipaddress, self.port)
        self.server_socket.bind(self.server_address)
        print 'listening on: '+ self.ipaddress
        
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
    def resetIndexesGivenFailedPacketResponse(self, sequenceNumber):
        sequenceNumber = 1
        self.packetNumber = self.failedPacketNumber
        self.startIndex = self.dataSize*self.failedPacketNumber
        self.endIndex = (self.dataSize*self.failedPacketNumber) + self.dataSize
        return sequenceNumber
    
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
    def checkFileNameIntegrity(self, address, data):
        try:
            self.fileSize = os.path.getsize(data)
            self.filename = data
            self.setDataSize(data)
            return True
        except OSError:
            self.server_socket.sendto('FNF', address)
            return False
    ############################################################################  
    ###
    ###Opens server socket to recieve initial file request from client
    ###
    ############################################################################           
    def listenForFileName(self):
        
        #Receive file request from client
        data, address = self.server_socket.recvfrom(1024)
        
        print 'File Request: ' + data
        if self.checkFileNameIntegrity(address, data):
            self.sendPackets(address)
        else:
            print 'File does not exist'
            self.listenForFileName()
    
    def checkConfirmationPacket(self, sequenceNumber):
        data = self.server_socket.recvfrom(1024)
        self.server_socket.settimeout(2)
        if data == sequenceNumber:
            return True
        else:
            return False
    
    def calculateCheckSum(self):
        return 0
    
    ############################################################################  
    ###
    ###Method that handles sending packets within the sliding window
    ###
    ############################################################################ 
    def sendPackets(self, address):
        sequenceNumber = 1
        
        while sequenceNumber <= 5:
            try:
                self.setIndexesForDataFetch()
                data = self.getPacketFromFile()
                packet = ({'sNum': sequenceNumber, 'pNum': self.packetNumber, 
                            'data': data, 'EOF' : self.endOfFile, 'checksum': 0 })
                            
                self.server_socket.sendto(str(packet).encode('utf-8'), address)
                print 'Sent: ' + str(packet['sNum'])
                
                response = self.server_socket.recvfrom(1024)
                print 'Received: ' + response[0]
                
                if self.endOfFile == '1':
                    break
                
                if sequenceNumber == 5:
                    sequenceNumber = 1
                    self.packetNumber += 1
                else:
                    sequenceNumber += 1
                    self.packetNumber += 1
            
            except socket.timeout:
                self.failedSeqNumber = sequenceNumber
                self.failedPacketNumber = self.packetNumber
                sequenceNumber = self.resetIndexesGivenFailedPacketResponse(self.failedPacketNumber)
            
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


    