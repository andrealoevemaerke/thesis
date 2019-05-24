#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 11:14:50 2019

@author: AndreaTram
"""

import numpy as np
from threading import Thread
import FFArithmetic as field
import shamir_scheme as ss
import time
import proc


#3 parties recieve shares from car's secrets
# car does the secrect splitting and reconstruction

# class for the car and another class for the parties?
# F = IntegerModP
# x= secret integer
# n= number of parties
# t= shamir degree


class server:
    securecom = {}
    broadcasts = {}
    def __init__(self,F, n, t, numTrip): 
        self.b = ss.share(F,np.random.choice([-1,1]), t, n)
        self.triplets = [proc.triplet(F,n,t) for i in range(numTrip)]
    #self.r, self.rb = proc.randomBitsDealer(F,n,t,l)
    
    
        
#class measurements:
    
  
    
class party(Thread):
        
    def __init__(self, F, n, t, i, s):  
        Thread.__init__(self)
        self.c = 0
        self.comr = 0
        self.F = F
        self.n = n
        self.t = t
        self.i = i
        self.server = s
        self.comtime = 0
        
#        
    def get_share(self, name):
        st = time.time()
        while True:
            try:
                res =  (self.server.securecom[name][self.i])
                break
            except:
                continue
        sl = time.time()
        self.comtime +=(sl-st)
        return res
    
    def add_shares(self,a,b):
        return a+b
    
    def mult_shares(self, a, b):
        r = self.server.triplets[self.c][self.i]
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
    
       
    def reconstruct_secret(self, c):
        res = []
        for i in range(self.n):
            res.append(self.get_broadcast(c + str(i)))
        return ss.rec(self.F, res)
    
    
    def broadcast(self, name, c):
        st = time.time()
        self.server.broadcasts[name + str(self.i)] = c
        sl = time.time()
        self.comtime += sl-st
    
    
    
    def get_broadcast(self, c):
        st = time.time()
        while True:
            try:
                res = self.server.broadcasts[c]
                break
            except:
                continue
        sl = time.time()
        self.comtime += (sl-st)
        return res
    
    def run(self):
        print(self.i)
## DISTRIBUTE INPUT
        #self.distribute_shares()
## GET INPUT SHARINGS FROM ALL PARTIES
        #input_shares = []
        #for i in range(self.n):
        x_share=self.get_share('x')
        u_share=self.get_share('u')
        t_share=self.get_share('TAU')
        y_share=self.get_share('UP')
        p_share=self.get_share('PSI')
        
        
        px= self.mult_shares(p_share,x_share)
        yu= self.mult_shares(y_share,u_share)
        
        sub_res=t_share-px-yu
      #  input_shares.append(self.get_share('x' + str(i)))
     #input_shares.append(self.get_share('x' + str(i)))
       ## sum_share = self.add_shares(x,y)
        #pro_share = self.mult_shares(x,y)
        #self.broadcast('s', sum_share)
        #print(self.reconstruct_secret('s'))       
        #print(sum_share)
        self.r = sub_res
        
    
    

class car:

    def __init__(self,F, x, u, TAU, UP, PSI, n, t,s):
        self.x = x      # measurement x
        self.u = u      # measurement y
    
        self.TAU = TAU 
        self.UP = UP
        self.PSI = PSI
        self.server = s
        self.F = F
        self.t = t
        self.n = n
    
    def distribute_shares(self,var, name):
        shares = ss.share(self.F, var, self.t, self.n)  # create shares
        
        s = name       # identify share
        st = time.time()
        self.server.securecom[s] = shares
        #sl = time.time()
        #self.comtime +=(sl-st)
           
    
    @staticmethod   
    def reconstruct_secret(F, c):
        #res = []
        
        
        #for i in range(self.n):
         #   res.append(self.(c+ str(i)))
        return ss.rec(F, c)
        
        
#class car: 
        
F = field.GF(979490791)            
n = 3
t = 1
x = 10
u = 2

TAU = 40
UP = 2
PSI = 3
serv = server(F, n, t, 3)


# TAU - PSI x - UP u
c=car(F, x, u, TAU, UP, PSI, n, t, serv)
c.distribute_shares (c.x,'x')
c.distribute_shares(c.u,'u')

c.distribute_shares(c.TAU,'TAU')
c.distribute_shares(c.UP,'UP')
c.distribute_shares(c.PSI,'PSI')

#print(car.reconstruct_secret(F,[5, 7, 12]))

#print(serv.securecom)
p1 = party(F,n,t,0, serv)
p2 = party(F,n,t,1, serv)
p3 = party(F,n,t,2, serv)

p1.start()
p2.start()
p3.start()


p1.join()
p2.join()
p3.join()


a=p1.r
b=p2.r
c=p3.r
#
print(a,b,c)
print(car.reconstruct_secret(F,[a,b,c]))