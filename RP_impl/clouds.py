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
      
      
m = 792606555396977# 7979490791
F = field.GF(m)            
n = 3
t = 1
x = 5

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

for i in range(n): 
    while True:
        try:
          sock.TCPclient(party_addr[i][0], party_addr[i][1], ['flag', 1])
          break
        except:
          time.sleep(1)
          continue
print('connection ok')

# all parties connected 
    

# shares from car has been recieved 

# other way to recieve shares: 

dic={}
dica2={}
dic_th={}
dictt={}
dicran={}
dicc={}


    

t_bo=True    
while t_bo==True: 
    
    if 'a1'+str(pnr) and 'a2'+str(pnr) and 'hh'+str(pnr) and 'tt'+str(pnr) and 'ran'+str(pnr)  and 'b0'+str(pnr) and 'b1'+str(pnr) and 'A00'+str(pnr) and 'A01'+str(pnr) and 'A10'+str(pnr) and 'A11'+str(pnr) and  'I00'+str(pnr) and 'I01'+str(pnr) and 'I10'+str(pnr) and 'I11'+str(pnr) not in dic.keys():  
       
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
        A00=(dic['A00'+str(pnr)])
        A01=(dic['A01'+str(pnr)])
        A10=(dic['A10'+str(pnr)])
        A11=(dic['A11'+str(pnr)])
        b0=(dic['b0'+str(pnr)])
        b1=(dic['b1'+str(pnr)])
        I00=(dic['I00'+str(pnr)])
        I01=(dic['I01'+str(pnr)])
        I10=(dic['I10'+str(pnr)])
        I11=(dic['I11'+str(pnr)])
      
        
        #print('sharea1:', sharea1)
        #print('sharea2:', sharea2)
        t_bo=False
            
   
          
print('recieved shares from car')
# shares has been recieved by clouds 
sum_result= sharea1+ sharea2

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
    

class party(Thread):
    def __init__(self, F, x, n, t, i, q, q2,q3, paddr, saddr):
        Thread.__init__(self)
        self.c = 0
        self.comr = 0
        self.recv = {}
        self.F = F
        self.x = x
        self.n = n
        self.t = t
        self.i = i
        self.q = q
        self.q2 = q2
        self.q3 = q3
        self.party_addr = paddr
        self.server_addr = saddr
        
    def distribute_shares(self, sec):
        shares = ss.share(self.F, sec, self.t, self.n)
        for i in range(self.n):
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['input' + str(self.i) , int(str(shares[i]))])
        
    def broadcast(self, name, s):
        for i in range(self.n):
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], [name + str(self.i) , int(str(s))])
                    
    def readQueue(self):
        while not self.q.empty():
            b = self.q.get()[1]
            self.recv[b[0]] = b[1]
            self.q3.put([b[0][-1], b[1]])
    
    def get_shares(self, name):
        res = []
        for i in range(self.n):
            while name + str(i) not in self.recv:
                self.readQueue()    
            res.append(self.F(self.recv[name+str(i)]))
            del self.recv[name + str(i)]
        return res
            
    def reconstruct_secret(self, name):
        return ss.rec(self.F, self.get_shares(name))
    
    def get_share(self, name):
        while name not in self.recv:
            self.readQueue()
        a = self.F(self.recv[name])
        del self.recv[name]
        return a
        
    def get_triplets(self):
        while 'triplets' not in self.recv:
            self.readQueue()
        b = self.recv['triplets']
        res = []
        for i in b:
            res.append([self.F(j) for j in i])
        self.triplets = res
    
    def mult_shares(self, a, b):
        r = self.triplets[self.c]
        self.c += 1
        
        d_local = a - r[0]
        self.broadcast('d' + str(self.comr), d_local)
        d_pub = self.reconstruct_secret('d' + str(self.comr))
        self.comr +=1
        
        e_local = b - r[1]
        self.broadcast('e' + str(self.comr), e_local)
        e_pub = self.reconstruct_secret('e' + str(self.comr))
        self.comr+=1
        
        return d_pub * e_pub + d_pub*r[1] + e_pub*r[0] + r[2]
    
    def legendreComp(self,a,b):
        r = self.triplets[self.c]
        self.c+=1
        t = self.tt
        g = a - b
        k = self.mult_shares(t, self.mult_shares(r[0], r[0]))
        j_loc = self.mult_shares(g, k)
        self.broadcast('j'+ str(self.comr), j_loc)
        j_pub = self.reconstruct_secret('j'+str(self.comr))
        self.comr+=1
        
        ex = (self.F.p-1)/2
        sym = pow(int(str(j_pub)),int(ex), self.F.p)
        f = sym * t
        c = self.mult_shares((f+1), self.F(2).inverse())
        return c
    
    def run(self):
        print('starting party ', self.i)
        self.get_triplets()
        #self.tt = self.get_share('b')
        
        # Niek protocol

        m = 2   # number of A rows
        nn = 2  # number of A coloums
        l = 1   # number of b rows
        mu=min(nn,m)


        L=np.array(([1,0],[11,1]))
        U=np.array(([1,8],[0,1]))


        A_matrix=np.array([[A00, A01], [A10, A11]])
        #print('A_matrix shares',A_matrix)
        b_vector=np.array([[b0],[b1]])
        I_2=np.array([[I00, I01], [I10, I11]])

        L=np.array(([1,0],[11,11]))
        U=np.array(([1,8],[0,1]))

        e00=np.array(U@A_matrix@L)
        #print('e00 result shares', e00)
        e01=np.array(U@b_vector)
        e10=np.array(I_2)
        e11=np.array(np.zeros((nn,l)))

        C_shares=np.array(([e00[0,0], e00[0,1], e01[0,0]],[e00[1,0], e00[1,1], e01[1,0]], [e10[0,0], e10[0,1], 0],[ e10[1,0], e10[1,1], 0]))
        #print('C matrix:', C_shares)
          
        f = []
        r_temp = []
        r = []
        
        for k in range(0, mu):
                
          broad_ckk= self.mult_shares(share_ran,C_shares[k,k])
          self.broadcast('c_kk' + str(self.comr), broad_ckk)
          
          # protocol line 5 
          r_temp.append(self.reconstruct_secret('c_kk'+str(self.comr))) 
          #print('r is:', r_temp)
          print('1print')
          if r_temp[k] == 0:
             r.append(0)
          elif r_temp[k] != 0:
             r.append(1)
          else: 
             print('error message')
          print('2print')   
          # protocol line 6:
          C_shares[mu+k,k] = shareh

          f.append(shareh)
   
          sharet = self.mult_shares(sharet,shareh)    # mult shares med Beavers

          
          # protocol line 9
          c_kk = (C_shares[k,k]+1-r[k])    # when c_kk !=0 then r will be 1 
                                           # and 1-r will cancel out
    
          shareh = self.mult_shares(shareh,c_kk)
          print('3PRINT')
          for i in range(0, mu+k):
              for j in range(k+1, nn+l):
                  if i!= k and (i<= mu or j <= nn-1):
                      # protocol line 13:
                      dummy=np.matrix( np.vstack((C_shares[i,j],-(C_shares[i,k]))))
                      temp= np.matrix(np.hstack(((C_shares[k,k]+1-r[k]), C_shares[k,j])))
                      temp_C1=self.mult_shares(temp[0,0],dummy[0,0]).n
                      temp_C2=self.mult_shares(temp[0,1],dummy[1,0]).n
                      C_shares[i,j]=temp_C1 +temp_C2 #manuel computation 1x2 2x1 = 1x1
                      print('if loop')          
          print('updated C:', C_shares[0,0])
        

        
p = party(F,int(x),n,t,pnr, q, q2, q3, party_addr, server_addr)
deal = dealer(F,n,t,50)
p.start()




#for k in range(mu):
  











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
