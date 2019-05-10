# -*- coding: utf-8 -*-
"""
Created on Wed May  8 10:24:06 2019
@author: pppc
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

party_addr = [
              ['192.168.100.4', 62], #cloud 1
              ['192.168.100.5', 62], #cloud 2
              ['192.168.100.6', 62], #cloud 3
              ['192.168.100.1', 62], #car
              ['192.168.100.2', 62], #not used
              ['192.168.100.3', 62] #not used
              ]

ccu_adr = '192.168.100.246'

server_addr = [
               [ccu_adr, 4050], #cloud 1
               [ccu_adr, 4060], #cloud 2
               [ccu_adr, 4061], #cloud 3
               [ccu_adr, 4031], #car 
               [ccu_adr, 4040], #not used
               [ccu_adr, 4041] #not used
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
# x = 5

ipv4 = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
pnr = party_addr.index([ipv4, port])
q = que.Queue()
q2 = que.Queue()
q3 = que.Queue()

print('pnr:', pnr)
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

for i in range(n): # n+1 to include car
    while True:
        try:
          sock.TCPclient(party_addr[i][0], party_addr[i][1], ['flag', 1])
          break
        except:
          time.sleep(1)
          continue
print('connection ok')
#p.start()
# all parties connected 
    

# shares from car has been recieved 

# other way to recieve shares: 
sharea1=[]  
sharea2=[] 
dica1={}
dica2={}
    
for i in range(n):
    print('i=',i)
    t=True    
    while t==True: 
        
        if 'a1'+str(i) not in dica1.keys():  
           
            while not q.empty():
                temp= q.get()
                
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                #if temp[1][0] == 'a1'+str(i)
                #print('temp is:', temp[1][0])
                #if 'a1'+str(i) in temp[1][0]
                 #   print('if entered')
                dica1[temp[1][0]]=temp[1][1] 
                print('dica1', dica1)
        else:
            sharea1.append(dica1['a1'+str(i)])
            print('sharea1:', sharea1)
            t=False
            
            
    t=True
    while t == True:
        if 'a2'+str(i) not in dica2.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                dica2[temp[1][0]]=temp[1][1] 
                print('dica2',dica2)
                
        else:
            sharea2.append(dica2['a2'+str(i)])
            t=False         
    print('first data ok')    
   
          
print('recieved shares from car')
# shares has been recieved by clouds 
           
#AA=np.array([[sharea1[pnv-1], sharea2[pnv-1]]])
sum_result= sum(sharea1[pnv-1], sharea2[pnv-1])

# send result to car
sock.TCPclient(party_addr[3][0], party_addr[3][1], ['output'+str(pnr) , int(str(sum_result))])
print('transmission')

                                                           
