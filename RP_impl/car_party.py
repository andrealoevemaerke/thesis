#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 13:05:07 2019

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
from numpy.linalg import matrix_rank




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
        print('name', name)
        while name not in self.recv:
            self.readQueue()
        a = self.F(self.recv[name])
        del self.recv[name]
        return a
    
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
        n=3
        m = 2   # number of A rows
        nn = 2  # number of A coloums
        l = 1   # number of b rows
        mu=min(nn,m)
    
        L=np.array(([1,0],[11,11]))
        U=np.array(([1,8],[0,1]))
        #print('car party ping 1')
        A00=2
        A01=3
        A10=4
        A11=9
        b0=6
        b1=15
        I00= 1
        I01= 0
        I10= 0
        I11= 1
        shareh=1
        sharet=1
        ran=7
        
        AA=np.array([[A00, A01],[A10, A11]])
        bb= np.array([[b0],[b1]])
        AB=np.hstack((AA,bb))
    
        rankAB=np.array(matrix_rank(AB))
        rankA= np.array(matrix_rank(AA))
        
        if rankA == rankAB:
            print('system is solvable')
        else:
            print('Preconditioning fails, system not solvable')
        
        s_A00= ss.share(self.F, A00, self.t, self.n)
        s_A01= ss.share(self.F, A01, self.t, self.n)
        s_A10= ss.share(self.F, A10, self.t, self.n)
        s_A11= ss.share(self.F, A11, self.t, self.n)
        s_b0= ss.share(self.F, b0, self.t, self.n)
        s_b1= ss.share(self.F, b1, self.t, self.n)
        s_h= ss.share(self.F, shareh, self.t, self.n)
        s_t= ss.share(self.F, sharet, self.t, self.n)
        s_r= ss.share(self.F, ran, self.t, self.n)
        s_I00=ss.share(self.F, I00, self.t, self.n)
        s_I01=ss.share(self.F, I01, self.t, self.n)
        s_I10=ss.share(self.F, I10, self.t, self.n)
        s_I11= ss.share(self.F, I11, self.t, self.n)
        
        #print('car party ping 2')
        for i in range(n):
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['hh'+str(i) , int(str(s_h[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['tt'+str(i) , int(str(s_t[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['ran'+str(i) , int(str(s_r[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['b0'+str(i) , int(str(s_b0[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['b1'+str(i) , int(str(s_b1[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['A00'+str(i) , int(str(s_A00[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['A01'+str(i) , int(str(s_A01[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['A10'+str(i) , int(str(s_A10[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['A11'+str(i) , int(str(s_A11[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['I00'+str(i) , int(str(s_I00[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['I01'+str(i) , int(str(s_I01[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['I10'+str(i) , int(str(s_I10[i]))])
            sock.TCPclient(self.party_addr[i][0], self.party_addr[i][1], ['I11'+str(i) , int(str(s_I11[i]))])
     
    #    print('car party ping 3')

        resx1= self.get_shares('x1')
        resx2= self.get_shares('x2')
        #print('shares from clouds:', resx1)
        x1_res=ss.rec(self.F, resx1)
        x2_res=ss.rec(self.F, resx2)
        #x1_res= self.reconstruct_secret(resx1)
#        x2_res= self.reconstruct_secret(resx2)
#        
#        
        res1=int(str(x1_res))
        res2=int(str(x2_res))
#   
        dummy3 =10E13
#        
#        
        if res1 > dummy3:
            res1 = res1 -792606555396977 
#            
        if res2 > dummy3:
            res2 = res2 -792606555396977 
#        
        finalX1=res1/10E10
        finalX2=res2/10E10
#        
        print('Solution:', finalX1, finalX2)

          
