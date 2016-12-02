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

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#IPADDR = raw_input("Enter IP address: ")
#PORT = raw_input("Enter PORT num: ")

IPADDR = '127.0.0.1'
PORT = '9876'
server_address = (IPADDR, int(PORT))

print'Starting server on: '+ IPADDR

server_socket.bind(server_address)

filename = ''
fileSize = 0

packetNumber = 0

isFileReadComplete = False
isFirstIteration = True
startIndex = 0
endIndex = 0
dataSize = 900

failedPacketNumber = 0
failedSeqNumber = 0
recievedFailedPacket = False

receivedPackets = []

################################################################################
### Clears fields when incorrect file is loaded
### @param: filename
### @param: isFirstIteration
################################################################################
def clearFileFields(filename, isFirstIteration):
    filename = ''
    isFirstIteration = False
    return filename, isFirstIteration
    
################################################################################
### Uses Indexes to load specific portions of the file
### @param: filename
### @param: start_index
### @param: end_index
### @param: isFileReadComplete
################################################################################
def getPackets(filename, startIndex, endIndex, isFileReadComplete):
    try:
        if endIndex > fileSize:
            endIndex = fileSize
            isFileReadComplete = True
        
        with open(filename) as fin:
            fin.seek(startIndex)
            data = fin.read(endIndex - startIndex)
        
        if '.jpg' in filename:
            data = data.encode('hex')
    except IOError as e:
        isFileReadComplete = False
        print 'file request: ' + filename
        raise Exception
    
    return data, isFileReadComplete

################################################################################
### Handles manipulating indexes, packet numbers and sequence numbers when the  
### server detects that the client did not receieve a package
### @param: sequenceNumber 
### @param: packetNumber
################################################################################
def checkFailedPacketResponse(sequenceNumber, packetNumber):
    if sequenceNumber == 5 and recievedFailedPacket:
        if failedSeqNumber == 1:
            sequenceNumber = 1
            packetNumber = packetNumber - 5
            startIndex = startIndex - (dataSize*5)
            endIndex = endIndex - (dataSize*5)
        else:
            sequenceNumber = 1
            packetNumber = failedPacketNumber - failedSeqNumber
            startIndex = startIndex - (dataSize*failedSeqNumber)
            endIndex = endIndex - (dataSize*failedSeqNumber)
    
    if sequenceNumber == 5 and not recievedFailedPacket:
        sequenceNumber = 1
    else:
        sequenceNumber += 1
        packetNumber += 1
    
    return sequenceNumber, packetNumber

################################################################################    
###
###Determines indexes for each file load
###
################################################################################
def setIndexesForDataFetch(isFirstIteration, startIndex, endIndex):
    if isFirstIteration:
        startIndex = 0
        endIndex = dataSize
        isFirstIteration = False
    else:
        startIndex += dataSize
        endIndex += dataSize
    return isFirstIteration, startIndex, endIndex

def checkFileNameIntegrity(filename, address):
    try:
        fileSize = os.path.getsize(filename)
        return fileSize
    except OSError:
        server_socket.sendto('FNF', address)
        

def listenForFileName():
        
    #Receive file request from client
    data, address = server_socket.recvfrom(1024)
        
    fileSize = checkFileNameIntegrity(data, address)
        
    #Fetch data size for indexing file loads
    filename = data
    try:
        fileSize = os.path.getsize(filename)
        sendPackets(filename, address, fileSize)
    except OSError:
        print 'File not found'
        listenForFileName()
        
def sendPackets(filename, address, fileSize):
    
    server_socket.settimeout(2)
    sequenceNumber = 1
    
    while sequenceNumber <= 5:
        isFirstIteration, startIndex, endIndex = setIndexesForDataFetch(isFirstIteration, startIndex, endIndex)
        data, isFileReadComplete = getPackets(filename, startIndex, endIndex, isFileReadComplete)
        
        packetNumber += 1
        
        packet = ({'seq_num': sequenceNumber, 'packet_number': packetNumber, 'data': data})
        
        server_socket.sendto(packet, address)
        
        
        
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
        
listenForFileName()


    