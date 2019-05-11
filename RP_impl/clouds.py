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
qA = que.Queue()

print('pnr:', pnr)
#Initialization..
#TCP_IP = '192.168.100.246'
#TCP_PORT = 62
UDP_PORT2 = 3000
server_info = party_addr[pnr]#(TCP_IP, TCP_PORT)
server2_info = (ipv4, UDP_PORT2)

# Create new threads..
t1_comms = commsThread(1, "Communication Thread", server_info,q)
#tA_comms = commsThread(1, "Communication Thread", server_info,qA)
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

dic={}
dica2={}
dic_th={}
dictt={}
dicran={}
dicc={}

sharea1=[]  
sharea2=[] 
shareh=[]
sharet=[]
share_ran=[]
A00_s= []
A01_s=[]
A10_s=[]
A11_s=[]
b0_s=[]
b1_s=[]
    

t_bo=True    
while t_bo==True: 
    
    if 'a1'+str(pnr) and 'a2'+str(pnr) and 'hh'+str(pnr) and 'tt'+str(pnr) and 'ran'+str(pnr)  and 'b0'+str(pnr) and 'b1'+str(pnr) and 'A00'+str(pnr) and 'A01'+str(pnr) and 'A10'+str(pnr) and 'A11'+str(pnr) not in dic.keys():  
       
        while not q.empty():
            temp= q.get()
            
            dic[temp[1][0]]=temp[1][1] 
            #print('dica1', dica1)
    else:
        sharea1=(dic['a1'+str(pnr)])
        sharea2=(dic['a2'+str(pnr)])
        shareh=(dic['hh'+str(pnr)])
        sharet=(dic['tt'+str(pnr)])
        share_ran=(dic['ran'+str(pnr)])
        A00_s=(dic['A00'+str(pnr)])
        A01_s=(dic['A01'+str(pnr)])
        A10_s=(dic['A10'+str(pnr)])
        A11_s=(dic['A11'+str(pnr)])
        b0_s=(dic['b0'+str(pnr)])
        b1_s=(dic['b1'+str(pnr)])
        b1_s=(dic['b1'+str(pnr)])
        
        #print('sharea1:', sharea1)
        #print('sharea2:', sharea2)
        t_bo=False
            
   
          
print('recieved shares from car')
# shares has been recieved by clouds 
print('type:', type(b1_s))           

sum_result= sharea1+ sharea2
#sum_th= sharet[0]+ shareh[0]

#b0=int(str(b0_s))
#b1=int(str(b1_s))
#A00=int(str(A00_s))
#A01=int(str(A01_s))
#A10=int(str(A10_s))
#A11=int(str(A11_s))

# Niek protocol
print('a element: ', A00_s)
#for i in range(n):
  #print('a element:' A00_s(i),)
A_matrix=np.array([[A00_s, A01_s], [A10_s, A11_s]])
print('A matrix: ',A_matrix)
print('AA matrix:' , A_matrix@A_matrix )
print('b0', b0_s)
print('b1', b1_s)
print('A00', A00_s)
print('A01', A01_s)
print('A10', A10_s)
print('A11', A11_s)

#print('AA matrix:', A_matrix@A_matrix)
  
#print(sum_result)
# send result to car
sock.TCPclient(party_addr[3][0], party_addr[3][1], ['output'+str(pnr) , int(str(sum_result))])
#sock.TCPclient(party_addr[3][0], party_addr[3][1], ['out_th'+str(pnr) , int(str(sum_th))])
print('transmission')


#for i in range(n): # n+1 to include car
    #while True:
        #try:
          #sock.TCPclient(party_addr[i][0], party_addr[i][1], ['flag', 1])
          #break
        #except:
          #time.sleep(1)
          #continue
#print('connection2 ok')
#for i in range(n):
    ##print('pnr is:',pnr)
    #sock.TCPclient(party_addr[i][0], party_addr[i][1], ['out_th'+str(pnr) , int(str(sum_th))])

#print('transmission2')
#share=[]  


#t_bo=True  

   
#for i in range(n):
    #while t_bo==True: 
        ##and 'out_th'+str(1) and 'out_th'+str(2) and 'a2'+str(1) and 'a2'+str(2) and 'hh'+str(1) and 'hh'+str(2) and 'tt'+str(1) and 'tt'+str(2) and 'ran'+str(1) and 'ran'+str(2) 
        #if 'out_th'+str(i)  and 'a2'+str(i) and 'hh'+str(i) and 'tt'+str(i)  and 'ran'+str(i) not in dicc.keys():   
            #while not q.empty():
                #temp2= q.get()
                #print('temp2:', temp2)
                ##print('temp', temp)
                ##print('temp_index0', temp[0])
                #dicc[temp2[1][0]]=temp2[1][1] 
                ##print(dicc)
                
        #else:
            #share.append(dicc['out_th'+str(i)])
            ##t_bo=False 

#print('recieve 2')      
#res_th=ss.rec(F, share)        
#print('th product:', res_th)                                                       
