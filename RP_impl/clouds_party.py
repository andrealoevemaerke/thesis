#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 13:33:06 2019

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
import matplotlib.pyplot as plt
import os


class party(Thread):
    def __init__(self, F, x, n, t, i, q, q2,q3, party_addr, server_addr):
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
        self.party_addr = party_addr
        self.server_addr = server_addr
        
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
        print('def ping 1')
        for i in range(self.n):
            print('def ping 1', i)
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

        
        m = 2   # number of A rows
        nn = 2  # number of A coloums
        l = 1   # number of b rows
        mu=min(nn,m)
        
        #
        L=np.array(([1,0],[11,1]))
        U=np.array(([1,8],[0,1]))
        
        print('Cloud ping 1')
        
        
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
      
        
               
                #print('sharea2:', sharea2)
                t_bo=False
        
        
        
        
        
        
        #input_sharesa00=self.get_share('A00').n  
        #print('share ping 1')       # reconstruct OK
        #input_sharesa01=self.get_share('A01').n
        #print('share ping 2')
        #input_sharesa10=self.get_share('A10').n
        #print('share ping 3')
        #input_sharesa11=self.get_share('A11').n
        #print('share ping 4')
        #input_sharesb0=self.get_share('b0').n
        #print('share ping 5')
        #input_sharesb1=self.get_share('b1').n
        #print('share ping 6')
        #h_share=self.get_share('hh').n
        #print('share ping 7')
        #t_share=self.get_share('tt').n
        #print('share ping 8')
        #ra_share=self.get_share('ran').n   # shares of random variable 
        #print('Cloud ping 2')

        #self.broadcast('AAA'+str(self.comr), input_sharesa00)
            print("Cloud ping 2")
            result=self.reconstruct_secret('AAA'+str(self.comr))
        
            print('Reconstruction of A00:', result)
        
        
        
        
        
        
        
        
        
