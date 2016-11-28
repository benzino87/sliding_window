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

IPADDR = '127.0.0.1'
PORT = 9876
server_address = (IPADDR, PORT)

print'Starting server on: '+ IPADDR

server_socket.bind(server_address)

isFirstIteration = True
filename = ''
fileSize = 0

packetNumber = 0
start_index = 0
end_index = 0
data_size = 900

def getPackets(filename, start_index, end_index):
    
    if end_index > fileSize:
        end_index = fileSize
        
    with open(filename) as fin:
        fin.seek(start_index)
        data = fin.read(end_index - start_index)

    return data
        
while True:
    
    sequenceNumber = 0
    
    #Receive file request from client
    data, address = server_socket.recvfrom(1024)
    
    if isFirstIteration:
        #Look for file requested and send to client
        filename = data
        fileSize = os.path.getsize(filename)
        isFirstIteration = False
        
    
    while sequenceNumber < 5:
    
        if sequenceNumber == 0:
            start_index = 0
            end_index = data_size
        else:
            start_index += data_size
            end_index += data_size
            
        data = getPackets(filename, start_index, end_index)
        packet = ({'seq_num': sequenceNumber,'packet_number': packetNumber, 'data': data})
        
        #debugging
        #print packet
        
        string_packet = str(packet)
        
        #print string_packet
        
        server_socket.sendto(string_packet, address)
        print 'Sent: ' + str(sequenceNumber)
        
        #Receive file request from client
        data, address = server_socket.recvfrom(1024)
        
        print 'Confirmation: ' + data
        
        sequenceNumber += 1
        packetNumber += 1
        
      
      
    #send data to client  
    
    



    