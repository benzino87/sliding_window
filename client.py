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

def requestNewFileName():
    filename = raw_input('Enter a file name: ')
    client_socket.sendto(filename, server_address)
    try:
        beginPacketHandling(filename)
    except Exception:
        requestNewFileName()
    
def writeFile(data, filename):
    file = open('writeFiles/'+filename, 'a+')
    file.write(data)
    file.close()

def beginPacketHandling(filename):
    while True:
        try:
            client_socket.settimeout(2)
            data, address = client_socket.recvfrom(1024)
            
            if data == 'FNF':
                print 'File Not Found'
                raise Exception
        
            data_length = len(data)
            
            dict_data = ast.literal_eval(data)
            
            writeFile(dict_data['data'], filename)
            
            print dict_data
            
            sequence_number = dict_data['seq_num']
            
            receivedSequenceNumbers.append(sequence_number)
            
            if (int(sequence_number) - previous_seq_num) < 0:
                client_socket.sendto('failed', server_address)
                
            received_packets.append(sequence_number)
            
            client_socket.sendto(str(sequence_number), server_address)
            
        except socket.timeout as packetError:
            print "Something went wrong"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#IPADDR = raw_input("Enter IP address: ")
#PORT = raw_input("Enter PORT num: ")

IPADDR = '127.0.0.1'
PORT = '9876'

server_address = (IPADDR, int(PORT))

received_packets = []

previous_seq_num = 1

receivedSequenceNumbers = []

hasPacketLoss = False

requestNewFileName()
