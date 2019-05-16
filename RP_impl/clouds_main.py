#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 13:28:28 2019

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
from clouds_party import party
import matplotlib.pyplot as plt
import os


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

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')

class plotter(Thread):
    def __init__(self,q):
      Thread.__init__(self)
#      self.line1 = []
      self.xdata = np.arange(0,100)
      self.y0 = np.zeros(100)-1
      self.y1 = np.zeros(100)-1
      self.y2 = np.zeros(100)-1
      self.y3 = np.zeros(100)-1
      self.q = q
      
    def run(self):
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        self.fig = plt.figure(figsize=(13,6))
        ax = self.fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line0, = ax.plot(self.y0,'bo',alpha=0.8)   
        line1, = ax.plot(self.y1,'ro',alpha=0.8) 
        line2, = ax.plot(self.y2,'go',alpha=0.8) 
        line3, = ax.plot(self.y3,'yo',alpha=0.8) 
        #update plot label/title
        plt.ylim(0,1)
        plt.ylabel('data')
        plt.xlabel('time')
        plt.title('Received data')
        plt.show()
        
        
        while True:
            if not self.q.empty():
                b = self.q.get()
                if b[0] == '0':
                    self.y0 = self.ploting(line0, self.y0, b[1])
                if b[0] == '1':
                    self.y1 = self.ploting(line1, self.y1, b[1])                                                                                                                                                                                              
                if b[0] == '2':
                    self.y2 = self.ploting(line2, self.y2, b[1])
                if b[0] == '3':
                    self.y3 = self.ploting(line3, self.y3, b[1])
            
    def ploting(self, line, ydata, y):
        if not isinstance(y, list):
            yl = ydata[:-1]
            ydata = np.insert(yl,0, y/float(m))

        else:
           return ydata
       
        # after the figure, axis, and line are created, we only need to update the y-data
        line.set_ydata(ydata)
        self.fig.canvas.draw()
        return ydata

class dealer():
    def __init__(self,F, n, t, numTrip):
        self.n = n
        b = ss.share(F,np.random.choice([-1,1]), t, n)
        self.distribute_shares('b', b)
        triplets = [proc.triplet(F,n,t) for i in range(numTrip)]
        for i in range(n):
            l = []
            for j in range(numTrip):
                l.append(triplets[j][i])
            sock.TCPclient(party_addr[i][0], party_addr[i][1], ['triplets' , l])
        
    def distribute_shares(self, name, s):
        for i in range(self.n):
            sock.TCPclient(party_addr[i][0], party_addr[i][1], [name , int(str(s[i]))])
    

m = 7979490791
F = field.GF(m)            
n = 3
t = 1
x = 5

ipv4 = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
pnr = party_addr.index([ipv4, port])
q = que.Queue()
q2 = que.Queue()
q3 = que.Queue()

#Initialization..
#TCP_IP = '192.168.100.246'
#TCP_PORT = 62
server_info = party_addr[pnr]#(TCP_IP, TCP_PORT)


# Create new threads..
t1_comms = commsThread(1, "Communication Thread", server_info,q)
#ploting = plotter(q3)
#ploting.start()
print('cloud main ping 1')
print(server_addr)



# Start new Threads
t1_comms.start()
p = party(F,int(x), t, pnr, q, q2, q3, party_addr, server_addr)

print('cloud main ping 2')
for i in party_addr:
    while True:
        try:
            sock.TCPclient(i[0], i[1], ['flag', 1])
            break
        except:
            time.sleep(1)
            continue
 
print('cloud main ping 3')       
deal = dealer(F,n,t,50)
p.start()
print('cloud main ping 4')
p.join()
print('cloud main ping 5')


