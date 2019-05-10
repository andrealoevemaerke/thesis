#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 10:39:22 2019

@author: AndreaTram
"""

import socket
import numpy as np
from threading import Thread
import FFArithmetic as field
import shamir_scheme as ss
import proc
import TcpSocket5 as sock
import time
import queue as que
from participantCodePLOT import party
import matplotlib.pyplot as plt
import os

port = 62

party_addr = [['192.168.100.1', 62], #P0  # car
              ['192.168.100.2', 62], #P1
              ['192.168.100.3', 62], #P2
              ['192.168.100.4', 62], #P3  # cloud
              ['192.168.100.5', 62], #P3  # cloud
              ['192.168.100.6', 62]  #P3  # cloud
              ]

ccu_adr = '192.168.100.246'

server_addr = [[ccu_adr, 4031], #P0
               [ccu_adr, 4040], #P1
               [ccu_adr, 4041], #P2
               [ccu_adr, 4050], #P3
               [ccu_adr, 4060], #Reciever 4
               [ccu_adr, 4061]  #Reciever 5
              ]


class commsThread (Thread):
   stop = False  
   def __init__(self, threadID, name, server_info,q):
      Thread.__init__(self)
      self.q = q
      self.threadID = threadID
      self.name = name
      self.server_info = server_info  # (Tcp_ip, Tcp_port)
      self.Rx_packet = [] # tuple [[client_ip, client_port], [Rx_data[n]]]

   def run(self):
#      print("Starting " + self.name)      
      #Create TCP socket
      tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      tcpsock.bind(tuple(self.server_info))
      #Communication loop - Wait->Receive->Put to queue
      while not self.stop:
         Rx_packet = sock.TCPserver(tcpsock)
#         print("Client info:",Rx_packet[0])
#         print("Data recv:",Rx_packet[1])
         if not self.q.full():
            self.q.put(Rx_packet)
      print("Exiting " + self.name)


m = 7979490791
F = field.GF(m)            
n = 3
t = 1
x = 5
y = 4

ipv4 = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
pnr = party_addr.index([ipv4, port])
q = que.Queue()
q2 = que.Queue()
q3 = que.Queue()
print('pnr:', pnr) # must be the car, 0



#Initialization..
#TCP_IP = '192.168.100.246'
#TCP_PORT = 62
UDP_PORT2 = 3000
server_info = party_addr[pnr]#(TCP_IP, TCP_PORT)
server2_info = (ipv4, UDP_PORT2)

# Create new threads..
t1_comms = commsThread(1, "Communication Thread", server_info,q)
#2_commsSimulink = UDPcommsThread(2, "t2_commsSimulink", server2_info)
#ploting = plotter(q3)
#ploting.start()
#p = party(F,int(x),n,t,pnr, q, q2, q3, party_addr, server_addr)

# Start new Threads
#t2_commsSimulink.start()
t1_comms.start()


# check for connection to clouds (4,5,6)
for i in range(3,6):
    while True:
        try:
          sock.TCPclient(party_addr[i][0], party_addr[i][1], ['flag', 1])
          break
        except:
          time.sleep(1)
          continue

print('connection ok')
#p.start()

# shares of a, b, h, t, r must be created
x_share=ss.share(F, x, t, n)
x=y
y_share=ss.share(F, x, t, n)

# send shares to clouds :
for i in range(3,6):
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['input'+str(pnr) , int(str(x_share[i-3]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['input'+str(pnr) , int(str(y_share[i-3]))])
    # dublere linje for alle shares eller skal der tjekkes for forbindelse hver gang?  



# computations in clouds here for a long time





# recieve shares from cloud of result
share=[]  
dic={}
t=True 

# modtage result shares
for i in range(3,6):
    t=True    
    while t==True: 
        if 'input'+str(i) not in dic.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                dic[temp[1][0]]=temp[1][1] 

        else:
            share.append(dic['input'+str(i)])
            t=False

print('share x:', share) 

# reconstruct solution x
print('recieve')      
result=ss.rec(F, share)        
print('Result is:', result)  
