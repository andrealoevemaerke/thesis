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

        input_sharesa00=self.get_share('A00'+str(self.i)).n  
        print('share ping 1')       # reconstruct OK
        input_sharesa01=self.get_share('A01'+str(self.i)).n
        print('share ping 2')
        input_sharesa10=self.get_share('A10'+str(self.i)).n
        print('share ping 3')
        input_sharesa11=self.get_share('A11'+str(self.i)).n
        print('share ping 4')
        input_sharesb0=self.get_share('b0'+str(self.i)).n
        print('share ping 5')
        input_sharesb1=self.get_share('b1'+str(self.i)).n
        print('share ping 6')
        h_share=self.get_share('hh'+str(self.i)).n
        print('share ping 7')
        t_share=self.get_share('tt'+str(self.i)).n
        print('share ping 8')
        ra_share=self.get_share('ran'+str(self.i)).n  # shares of random variable 
        print('Cloud ping 9')
        input_sharesI00=self.get_share('I00'+str(self.i)).n  
        print('share ping 10')       # reconstruct OK
        input_sharesI01=self.get_share('I01'+str(self.i)).n
        print('share ping 11')
        input_sharesI10=self.get_share('I10'+str(self.i)).n
        print('share ping 12')
        input_sharesI11=self.get_share('I11'+str(self.i)).n

        self.broadcast('AAA'+str(self.comr), input_sharesa00)
        print("Cloud ping 2")
        result=self.reconstruct_secret('AAA'+str(self.comr))
        
        print('Reconstruction of A00:', result)
        
        
        # Gaussian Elimination without pivoting
        
        AA=np.array([[input_sharesa00, input_sharesa01],[input_sharesa10, input_sharesa11]]) 
        bb= np.array([[input_sharesb0],[input_sharesb1]])
        I_n=np.array([[input_sharesI00, input_sharesI01],[input_sharesI10, input_sharesI11]])
        
        print('matrix form ok')
        
        #print('U type',type(U[0,0]))
        #print('AA type',type(AA[0,0]))
        #print('L type',type(L[0,0]))
        e11= np.array(U@AA@L)
        e12=np.array(U@bb)         
        e21= np.array(I_n)
        e22= np.array(np.zeros((nn,l)))
        
        print('C elements construction ok')
        
        self.broadcast('e11'+str(self.comr), e11[0,0])
        print("Cloud ping 2")
       # res_C=self.reconstruct_secret('e11'+str(self.comr))
        #print('e11 reconstruct', res_C) # ok 
        
        C_shares=np.array(([e11[0,0], e11[0,1], e12[0,0]],[e11[1,0], e11[1,1], e12[1,0]], [e21[0,0], e21[0,1], 0],[ e21[1,0], e21[1,1], 0]))
        C_shares=C_shares.astype(int)

   
        self.broadcast('e11'+str(self.comr), C_shares[0,0])
   
        res_C=self.reconstruct_secret('e11'+str(self.comr))
        print('C00 reconstruct', res_C)
 
       
        f = []
        r_temp = []
        r = []
        
        for k in range(mu):
                
            broad_ckk= self.mult_shares(ra_share,C_shares[k,k]).n
            self.broadcast('c_kk' + str(self.comr), broad_ckk)
            f.append(self.reconstruct_secret('c_kk'+str(self.comr)))
            self.comr=+1
            print('C_kk reconstruct', f)
        
