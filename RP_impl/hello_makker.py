
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

port = 65

party_addr = [['192.168.100.1', 65], #P0
              ['192.168.100.2', 65], #P1
              ['192.168.100.3', 65], #P2
              ['192.168.100.4', 65], #P3
              ['192.168.100.5', 65], #P3
              ['192.168.100.6', 65]  #P3
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
n = 4
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
            
