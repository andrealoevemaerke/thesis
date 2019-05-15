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
from numpy.linalg import matrix_rank
#from scipy import linalg
#from scipy.linalg import toeplitz
#from numpy.linalg import inv
import random 
from threading import Thread
#


port = 62

party_addr = [
              ['192.168.100.4', 62], # cloud1
              ['192.168.100.5', 62], # cloud2
              ['192.168.100.6', 62], # cloud3
              ['192.168.100.1', 62], # car
              ['192.168.100.2', 62], #P1
              ['192.168.100.3', 62] #P2
              ]

ccu_adr = '192.168.100.246'

server_addr = [
               [ccu_adr, 4050], #cloud 1
               [ccu_adr, 4060], #cloud 2
               [ccu_adr, 4061], #cloud 3
               [ccu_adr, 4031], #car
               [ccu_adr, 4040], #P1
               [ccu_adr, 4041] #P2
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


m = 792606555396977 #7979490791
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
for i in range(n):
    while True:
        try:
          sock.TCPclient(party_addr[i][0], party_addr[i][1], ['flag', 1])
          break
        except:
          time.sleep(1)
          continue

print('connection ok')
#p.start()

m = 2   # number of A rows
nn = 2  # number of A coloums
l = 1   # number of b rows
mu=min(nn,m)
AA= np.array([[2, 3], [4 , 9]])      # A, secret
bb= np.array([[6],[15]])             # b, secret
iden_n=np.identity(nn)

AB=np.hstack((AA,bb))

rankAB=np.array(matrix_rank(AB))
rankA= np.array(matrix_rank(AA))

if rankA == rankAB:
    print('system is solvable')
else:
    print('Preconditioning fails, system not solvable')
L=np.array(([1,0],[11,11]))
U=np.array(([1,8],[0,1]))
ran=7

#L = toeplitz([1,random.randint(1,10)])  
#U = toeplitz([1,random.randint(1,10)])
    
#L= np.array(np.tril(L) )               # remove upper triangular entries
#U= np.array(np.triu(U) )               # remove lower triangular entires
    
#ran= random.randint(1,51)
#iden= 0

#
#l11=L[0][0]
#l12=L[0][1]
#l21=L[1][0]
#l22=L[1][1]
#u11=U[0][0]
#u12=U[0][1]
#u21=U[1][0]
#u22=U[1][1]
hh= 1
tt= 1
iden_22=np.identity(nn)





# shares of a, b, h, t, r must be created
a1_share=ss.share(F, x, t, n)
a2_share= ss.share(F, y, t, n)




#b_share=np.zeros((2,1))
#A_share=np.zeros((2,2))
#iden_share= np.zeros((2,2))


b=bb[0]
b=int(b)
b0_share=ss.share(F, b, t, n)

b=bb[1]
b=int(b)
b1_share=ss.share(F, b, t, n)

A= AA[0,0]
A= int(A)
A00_share=ss.share(F, A, t, n)

A= AA[0,1]
A= int(A)
A01_share=ss.share(F, A, t, n)

A= AA[1,0]
A= int(A)
A10_share=ss.share(F, A, t, n)

A= AA[1,1]
A= int(A)
A11_share=ss.share(F, A, t, n)


II= iden_22[0,0]
II= int(II)
I00_share=ss.share(F, II, t, n)

II= iden_22[0,1]
II= int(II)
I01_share=ss.share(F, II, t, n)

II= iden_22[1,0]
II= int(II)
I10_share=ss.share(F, II, t, n)

II= iden_22[1,1]
II= int(II)
I11_share=ss.share(F, II, t, n)

h_share= ss.share(F, hh, t, n)
t_share= ss.share(F, tt, t, n)
ran_share=ss.share(F, ran, t, n)


print('constructed shares in car')
# send shares to clouds :
for i in range(n):
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['a1'+str(i) , int(str(a1_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['a2'+str(i) , int(str(a2_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['hh'+str(i) , int(str(h_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['tt'+str(i) , int(str(t_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['ran'+str(i) , int(str(ran_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['b0'+str(i) , int(str(b0_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['b1'+str(i) , int(str(b1_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['A00'+str(i) , int(str(A00_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['A01'+str(i) , int(str(A01_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['A10'+str(i) , int(str(A10_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['A11'+str(i) , int(str(A11_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['I00'+str(i) , int(str(I00_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['I01'+str(i) , int(str(I01_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['I10'+str(i) , int(str(I10_share[i]))])
    sock.TCPclient(party_addr[i][0], party_addr[i][1], ['I11'+str(i) , int(str(I11_share[i]))])
# dublere linje for alle shares eller skal der tjekkes for forbindelse hver gang?  
print('car has send shares')


# computations in clouds here for a long time





# recieve shares from cloud of result
share_res=[]
th_res=[]
share_th=[]
dic_res={}
boo=True 

# modtage result shares
for i in range(n):
    boo=True    
    while boo==True: 
        if 'output'+str(i)  not in dic_res.keys():   
            while not q.empty():
                temp= q.get()
                #print('temp', temp)
                #print('temp_index0', temp[0])
                #print('temp_index1', temp[1])
                dic_res[temp[1][0]]=temp[1][1]
                #dic_res[temp[1][0]]=temp[1][1]

        #elif 'output'+str(i) and 'out_th'+str(i) in dic_res.keys():
            
        else:
            share_res.append(dic_res['output'+str(i)])
            #share_th.append(dic_res['out_th'+str(i)])
            #th_res.append(dic_res['out_th'+str(i)])
            boo=False

#print('share x:', share) 

# reconstruct solution x
print('recieve')      
result=ss.rec(F, share_res)        
print('Result is:', result)
#result_th=ss.rec(F,share_th)
#print('Product th is:', result_th)
#
#res_tthh=ss.rec(F, th_res)
#print('th sum is:',res_tthh)
