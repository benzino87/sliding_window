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

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#IPADDR = raw_input("Enter IP address: ")
#PORT = raw_input("Enter PORT num")

IPADDR = '127.0.0.1'
PORT = 9876
server_address = (IPADDR, PORT)

print'Starting server on: '+ IPADDR

server_socket.bind(server_address)

isFirstIteration = True
isFileReadComplete = False
filename = ''
fileSize = 0

packetNumber = 1

start_index = 0
end_index = 0
data_size = 900

failedPacketNumber = 0
failedSeqNumber = 0
recievedFailedPacket = False

received_packets = []

################################################################################
### Uses Indexes to load specific portions of the file
### @param: filename
### @param: start_index
### @param: end_index
### @param: isFileReadComplete
################################################################################
def getPackets(filename, start_index, end_index, isFileReadComplete):
    
    if end_index > fileSize:
        end_index = fileSize
        isFileReadComplete = True
        
    with open(filename) as fin:
        fin.seek(start_index)
        data = fin.read(end_index - start_index)

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
            start_index = start_index - (data_size*5)
            end_index = end_index - (data_size*5)
        else:
            sequenceNumber = 1
            packetNumber = failedPacketNumber - failedSeqNumber
            start_index = start_index - (data_size*failedSeqNumber)
            end_index = end_index - (data_size*failedSeqNumber)
    
    if sequenceNumber == 5 and not recievedFailedPacket:
        sequenceNumber = 1
    else:
        sequenceNumber += 1
        packetNumber += 1
    
    return sequenceNumber, packetNumber
    
        
while True:
    
    #Receive file request from client
    data, address = server_socket.recvfrom(1024)
    
    if isFirstIteration:
        #Look for file requested and send to client
        filename = data
        fileSize = os.path.getsize(filename)
        isFirstIteration = False
    
    sequenceNumber = 1
    
    while sequenceNumber <= 5:
    
        if sequenceNumber == 1:
            start_index = 0
            end_index = data_size
        else:
            start_index += data_size
            end_index += data_size
            
        data, isFileReadComplete = getPackets(filename, start_index, end_index, isFileReadComplete)
        
        packet = ({'seq_num': sequenceNumber,'packet_number': packetNumber, 'data': data})
        
        #debugging
        #print packet
        
        string_packet = str(packet)
        
        #print string_packet
        
        server_socket.sendto(string_packet, address)
        print 'Sent: ' + str(sequenceNumber)
        
        #Receive file request from client
        confirmation_data, address = server_socket.recvfrom(1024)
        
        print 'Confirmation: ' + confirmation_data
        
        #Check for packet failed notification
        if confirmation_data == 'failed':
            failedPacketNumber = packetNumber
            failedSeqNumber = sequenceNumber
            recievedFailedPacket = True
        
        received_packets.append(confirmation_data)
        
        sequenceNumber, packetNumber = checkFailedPacketResponse(sequenceNumber, packetNumber)
        
        if isFileReadComplete and not recievedFailedPacket:
            break
    if isFileReadComplete and not recievedFailedPacket:
            break
    



    