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

party_addr = [['192.168.100.1', 62], #car
              ['192.168.100.4', 62], #cloud 1
              ['192.168.100.5', 62], #cloud 2
              ['192.168.100.6', 62]  #cloud 3
              ['192.168.100.2', 62], #not used
              ['192.168.100.3', 62], #not used
              ]

ccu_adr = '192.168.100.246'

server_addr = [[ccu_adr, 4031], #car 
               [ccu_adr, 4050], #cloud 1
               [ccu_adr, 4060], #cloud 2
               [ccu_adr, 4061]  #cloud 3
               [ccu_adr, 4040], #not used
               [ccu_adr, 4041], #not used
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

for i in range(n+1):
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

dic1={}
dic2={}
dic3={}
share1=[]
share2=[]
share3=[]

# recieve share from car now
print('pnr:', pnr)



if pnr == 1:
   t=True    
    while t==True: 
        if 'input'+str(pnr) not in dic.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                dic1[temp[1][0]]=temp[1][1] 
                
        else:
            share1.append(dic1['input'+str(pnr)])
            t=False

elif pnr ==2:
   t=True    
    while t==True: 
        if 'input'+str(pnr) not in dic.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                dic2[temp[1][0]]=temp[1][1] 
                
        else:
            share2.append(dic2['input'+str(pnr)])
            t=False
            
elif pnr ==3:
    t=True    
    while t==True: 
        if 'input'+str(pnr) not in dic.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                dic3[temp[1][0]]=temp[1][1] 
                
        else:
            share3.append(dic3['input'+str(pnr)])
            t=False
   
else:
    print('Fail')    

# shares from car has been recieved 

# other way to recieve shares: 
share=[]  
dic={}
t=True     
for i in range(1,4): # range skal passe til forskellige værdier bilen sender
# skal sikre hvis append bruges at rækkefølge af værdier er fast så data ikke mixes
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
           

# shares has been recieve by clouds 
           
#print('share:', share1)           
#share_sum=sum(share)

for i in range(n+1):
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['output'+str(pnr) , int(str(share_sum))])
print('transmission')
share=[]  

for i in range(n+1):
    t=True    
    while t==True: 
        if 'output'+str(i) not in dic.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                dic[temp[1][0]]=temp[1][1] 
                
        else:
            share.append(dic['output'+str(i)])
            t=False    
print('recieve')      
result=ss.rec(F, share)        
print('Result is:', result) 


x_share=ss.share(F, x, t, n)
for i in range(n+1):
