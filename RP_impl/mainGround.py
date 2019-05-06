

import socket
import numpy as np
from threading import Thread
import FFArithmetic as field
import shamir_scheme as ss
import proc
import TcpSocket5 as sock
import time
import queue as que
from cloud_code import party
import os
import time
from scipy import linalg
from scipy.linalg import toeplitz
from numpy.linalg import inv
import random 
from numpy.linalg import matrix_rank
from threading import Thread
import FFArithmetic as field

port = 62

party_addr = [['192.168.100.1', 62], #P0 -- NO PLOT
              ['192.168.100.2', 62], #P1
              ['192.168.100.3', 62], #P2
              ['192.168.100.4', 62], #P3 -- NOT PLOT
              ['192.168.100.5', 62], #Receiver 4
              ['192.168.100.6', 62], #Reciever 5
              ]

ccu_adr = '192.168.100.246'

server_addr = [[ccu_adr, 4010], #P0
               [ccu_adr, 4011], #P1
               [ccu_adr, 4030], #P2
               [ccu_adr, 4031],               #P3
               [ccu_adr, 4040],               #Reciever 4
               [ccu_adr, 4041]                #Reciever 5
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
mm = 97
#F = field.GF(m)            
n = 4 
t = 1
x = 5 #np.random.randint(0,50,40)

F = field.GF(792606555396977)   # prime, if larger the variables overfloat
								# if smaller, the scaling must be smaller to 
								# to be within the field and the precision 
								# decreases too much to return correct output
				 
#n = 3
#t = 1
#serv = server(F, n, t, 1500)

# Matrix dimensions
m = 2   # number of A rows
nn = 2  # number of A coloums
l = 1   # number of b rows
mu=min(nn,m)

# Protocol inputs 
A= 0 # initialize
b= 0 # initialize

tt = 1      # secret
hh = 1      # secret

# Secret matrices, input
H= np.array([[2, 3], [4 , 9]])      # A, secret
G= np.array([[6],[15]])             # b, secret
iden_n=np.identity(nn)
    
AB=np.hstack((H,G))

rankAB=np.array(matrix_rank(AB))
rankA= np.array(matrix_rank(H))

#    if rankA==rankAB:
#        print('System is solvable')
#    else:
#        print('Preconditioning fails, system not solvable')
#    
# Generate Upper/Lower Toeplitz matrices (open)
# OBS: random variables small range due to overfloat caused by scaling  
# to avoid floats when inverting

L = toeplitz([1,random.randint(1,10)])  
U = toeplitz([1,random.randint(1,10)])

L= np.array(np.tril(L) )               # remove upper triangular entries
U= np.array(np.triu(U) )               # remove lower triangular entires

ran= random.randint(1,51)
iden= 0

# Generate random vector (open)   

z = np.random.randint(1,100,(1,m))

# create shares of each matrix entry
gr=ground(F, A, b, hh, tt, iden, ran, n, t, server_info) #serv) # hh, tt)

for p in range(0, m):
	b=G[p]
	b=int(b)

	gr.distribute_shares(b,'b'+str(p))

	
	for q in range(0, nn):
		A=H[p,q]
		A=int(A)
		iden_ny=iden_n[p,q]
		iden_ny=int(iden_ny)

		gr.distribute_shares(A,'a'+str(p)+str(q))
		gr.distribute_shares(iden_ny,'iden'+str(p)+str(q)) 
		
gr.distribute_shares(gr.hh,'h_shares') #hh
gr.distribute_shares(gr.tt,'t_shares') #tt
gr.distribute_shares(gr.ran,'ran_shares') #tt

ipv4 = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
pnr = party_addr.index([ipv4, port])
q = que.Queue()
q2 = que.Queue()
q3 = que.Queue()

#Initialization..
#TCP_IP = '192.168.100.246'
#TCP_PORT = 62
#UDP_PORT2 = 3000
server_info = party_addr[pnr] #(TCP_IP, TCP_PORT)
#server2_info = (server_info[0], UDP_PORT2)

# Create new threads..
t1_comms = commsThread(1, "Communication Thread", server_info,q)
#t2_commsSimulink = UDPcommsThread(2, "t2_commsSimulink", server2_info)

##p = party(F,int(x),n,t, pnr, q, q2, party_addr, server_addr)

# Start new Threads
#t2_commsSimulink.start()
t1_comms.start()

#for i in party_addr:
    #while True:
     #   try:
    #        sock.TCPclient(i[0], i[1], ['flag', 1])
   #         break
  #      except:
 #           continue

#deal = dealer(F,n,t,50)
#p.start()




while True:
  try:
      sock.TCPclient(party_addr[4][0], party_addr[4][1], ['flag', 1])
      break
  except:
      time.sleep(1)
  continue

#p.start()


sock.TCPclient(party_addr[4][0], party_addr[4][1], ['output' , int(str(32))])
            
while True: 
      if not q.empty():
            print(q.get())



