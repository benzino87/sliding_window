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
        self.receivedPackets = []
        self.previousSeqNum = 1
        self.receivedSequenceNumbers = []
        self.hasPacketLoss = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (self.ipaddress, self.port)
        
        
    def requestNewFileName(self):
        filename = raw_input('Enter a file name: ')
        self.client_socket.sendto(filename, self.server_address)
        try:
            self.beginPacketHandling(filename)
        except Exception as e:
            print e
            # self.requestNewFileName()
    
    def writeFile(self, data, filename):
        file = open('writeFiles/'+filename, 'a+')
        file.write(data)
        file.close()
        
    def parsePacketData(self, bytes):
        packetData = ast.literal_eval(bytes)
        data = packetData['data']
        sequenceNumber = packetData['sNum']
        packetNumber = packetData['pNum']
        endOfFile = packetData['EOF']
        dataLength = len(packetData)
        print packetData
        return data, sequenceNumber, packetNumber, endOfFile, dataLength
    ############################################################################
    ###
    ###TODO check for all files
    ###closes socket when file transfer is complete
    ###@param: endOfFile
    ###
    ############################################################################
    def checkFileIntegrityWithEndFileFlag(self, endOfFile):
        if endOfFile == '1':
            self.client_socket.close()
            return True
        else:
            return False
    
    def beginPacketHandling(self, filename):
        while True:
            try:
                self.client_socket.settimeout(2)
                bytes, address = self.client_socket.recvfrom(1024)
                
                if bytes == 'FNF':
                    print 'File Not Found'
                    raise Exception
                
                data, sequenceNumber, packetNumber, endOfFile, dataLength = self.parsePacketData(bytes)
                self.writeFile(data, filename)
                self.receivedSequenceNumbers.append(sequenceNumber)
                self.receivedPackets.append(packetNumber)
                
                if self.checkFileIntegrityWithEndFileFlag(endOfFile):
                    break
                
        
                # if (int(sequence_number) - previous_seq_num) < 0:
                #     client_socket.sendto('failed', server_address)
                #self.client_socket.sendto(str(sequence_number), self.server_address)
                
            except socket.timeout as packetError:
                print "Something went wrong"



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