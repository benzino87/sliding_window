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

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

IPADDR = '127.0.0.1'
PORT = 9876

server_address = (IPADDR, PORT)

filename = raw_input('Enter a file name: ')

print filename

received_packets = []

client_socket.sendto(filename, server_address)

previous_seq_num = 1

def writeFile(data):
    
    file = open('writeFiles/'+filename, 'a+')
    file.write(data)
    file.close()

while True:
    
    data, address = client_socket.recvfrom(1024)

    data_length = len(data)
    
    dict_data = ast.literal_eval(data)
    
    writeFile(dict_data['data'])
    
    print dict_data
    
    sequence_number = dict_data['seq_num']
    
    if (int(sequence_number) - previous_seq_num) < 0:
        client_socket.sendto('failed', server_address)
        
    received_packets.append(sequence_number)
    
    client_socket.sendto(str(sequence_number), server_address)