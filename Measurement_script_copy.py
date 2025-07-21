# -*- coding: utf-8 -*-
"""
Created on Wed Jul 09 15:24:16 2025

@author: manip.ubt
"""
#%% Syntax
#When inputing values for frequency keep in mind 10^9 is written as E9

import pyvisa
import numpy as np
import time
#import zhinst.utils
import pandas as pd
#from scipy.signal import find_peaks

#%% defines the class and functions for vna
#VNA = MS46522B('TCPIP0::192.168.1.7::inst0::INSTR')

class MS46522B:
    def __init__(self ,device):
        rm = pyvisa.ResourceManager()
        self.MS46522B = rm.open_resource(device)
        print(self.MS46522B.query('*IDN?'))
    
    def read_S(self):
        return self.MS46522B.query(':CALC1:DATA:SDAT?') # Requests data on the S value
    
    def read_f(self):
        return self.MS46522B.query(':SENS1:FREQ:DATA?') # Requests data on the frequency value*
    
    def trig(self):
        self.MS46522B.write(':TRIG:SING') # Triggers a sweep to run
        
    def __del__(self):
        print("closed previous communication channel with MS46522B") # Tells the system to terminate connection
        self.MS46522B.close()

    def hold(self):
        self.MS46522B.write(':SENS1:HOLD:FUNC HOLD') # Tells VNA to hold and pause continous measurements
        
    def S1_power(self,power):
        self.MS46522B.write(':SOUR1:POW:PORT1 '+str(power)) # Adjusts the power on source 1 through port#, adjusting to power##
        
    def f_start(self, frequency):
        self.MS46522B.write(':SENSe1:FREQuency:STARt '+str(frequency)) #defines inital boundary
        
    def f_end(self, frequency): # Defines final boundary
        self.MS46522B.write(':SENSe1:FREQuency:STOP '+str(frequency))
    
    def Display_no(self,number): # Number varies from 1-4 and changes the number of displays set up on monitor
        self.MS46522B.write(':DISPlay:COUNt '+str(number))
        
    def continous(self):
        self.MS46522B.write(':SENSe1:HOLD:FUN CONT')
        
    def average(self,NRF):
        self.MS46522B.write(':SENSe1:AVERAGE:COUNt '+str(NRF)) # This function defines the number of measured averages per point
        
        
# =============================================================================
# Start up commands for initializing  vna
# p. 99 Example General setup
# p. 100 Example Frequency and sweep settings and number of points
# 
# p. 699
# :SOUR1:POW:PORT1 -30
# :SOUR1:POW:PORT1?
# 
# p. 723
# :SENSe{1-16}:HOLD:FUNC HOLD and :TRIG:SING
# 
# p. 705 Status subsystem
# p. 113 Read status byte
# 
# p.274
# :CALC1:DATA:SDAT?
# 
# p.627
# :SENSe{1-16}:FREQuency:DATA?
# 
# p.437-438
# :SENS1:AVER:COUN 2
# :SENS1:AVER ON
# 
# 
# Initialize after preset:
# :DISPlay:COUNt 1;:CALCulate1:PARameter:COUNt 1;:DISPlay:WINDow1:SPLit R1C1;:CALCulate1:PARameter1:DEFine S11
# :SOUR1:POW:PORT1 -30;:SOUR1:POW:PORT2 -30;:SENSe1:FREQuency:STARt 3.0E9;:SENSe1:FREQuency:STOP 8.0E9;:SENSe1:SWEep:POINt 2001
# :SENS1:HOLD:FUNC HOLD
# :SENS1:AVER:COUN 10
# :SENS1:AVER ON
# 
# Make a frequency sweep:
# :TRIG:SING
# 
# Acquire S parameter:
# :CALC1:DATA:SDAT?
# 
# Acquire frequencies:
# :SENS1:FREQ:DATA?
# =============================================================================
         
#%% defines the class and functions for spectrum analyzer
class N9020A:
    #
    def __init__(self ,device):
        rm = pyvisa.ResourceManager()
        self.N9020A = rm.open_resource(device)
        print(self.N9020A.query('*IDN?'))  #communicates to your device to make sure you can still see it
   
    def set_cent_freq(self,cent_freq):
        self.N9020A.write('FREQ:CENT'+' '+str(cent_freq)) #defines in terms of Hertz the position for the center point of FSP
        
    def read_cent_freq(self):
        return self.N9020A.query('FREQ:CENT?') #reads out the current point
    
    def set_span(self,span):
        self.N9020A.write('FREQ:SPAN'+' '+str(span))  #Tells the system what broadband to look over
        
    def read_span(self):
        return self.N9020A.query('FREQ:SPAN?') # Reads out the current span
    
    def set_bw(self,bw):
        self.N9020A.write('BAND'+' '+str(bw)) 

    def read_bw(self):
        return self.N9020A.query('BAND?')
    
    def set_sweep_points(self,points):
        self.N9020A.write('SWE:POIN'+' '+str(points))

    def read_sweep_points(self):
        return self.N9020A.query('SWE:POIN?')
    
    def average_state(self, onoff):
        self.N9020A.write('AVER:STAT'+' '+str(onoff))
        
    def average_number(self, number):
        self.N9020A.write('AVER:COUN'+' '+str(number))   
        
    def single_trace(self,timeout=200000):
        self.N9020A.write('INIT:CONT OFF')
        self.N9020A.write('INIT:IMM')
        result = 0 
        cnt = 0
        while True:
            try:
                result = int(self.N9020A.query("*OPC?"))
            except (pyvisa.VisaIOError):
                pass
            if result == 1 or cnt > timeout*10:
                break
            cnt+=1
        time.sleep(0.1)   
        datas = self.N9020A.query('FETCh:SANalyzer1?')
        self.N9020A.write('INIT:CONT ON')
        return np.reshape(np.array(datas.split(','),dtype=float),(-1,2))
    
    def peak_search(self):
        self.N9020A.write('CALC:MARK1:MAX')
        return self.N9020A.query('CALC:MARK1:X?')
    
    def __del__(self):
        print("closed previous communication channel with N9020A")
        self.N9020A.close()

#FSP=N9020A('TCPIP0::192.168.1.6::inst0::INSTR')
#%% initial sweep setting
VNA = MS46522B('TCPIP0::192.168.1.7::inst0::INSTR')
VNA.S1_power(10) # Used to pick power for a broad sweep
VNA.f_start(5.85E9) # Denotes starting bounday for broad sweep
VNA.f_end(6E9) # Denotes final boundary for broad sweep

VNA.trig() 

#If chaning broad sweep boundaries return to inital values or note to what value boundaries have
#shifted
#%% Peak finder


FSP.set_cent_freq(1118349664.8)
FSP.set_span(10000)
#f=float(FSP.peak_search())

#FSP.set_cent_freq(f)
#FSP.set_span(1000) 5098349664.8


#%% Resonance VNA
    
VNA.S1_power(-15)
VNA.f_start(5.0966E9)
VNA.f_end(5.097E9)

#%%

#VNA.S1_power(-15)
VNA.f_start(5.0967E9)
VNA.f_end(5.0969E9)


#%%
VNA.f_start(5.972E9)
VNA.f_end(5.974E9)

#%% 

VNA.average(400)
VNA.trig()

#%%

FSP.average_number(1)
#FSP.single_trace()

#%% notes on previous settings
Power= [-43,-38,-33,-28]
Cavity_Resonance_GHz=[5.09678041, 5.096783502, 5.096786587,5.096783942]
shifted_cavity=[5.096825410,5.096825422, 5.098308700]
shifted_power=[-28,-23,-20]
Mechanical_Resoance_GHz=[5.0983051742, 5.098308264, 5.096825430]
shifted_mech=[5.098350179,5.098350179,5.098350197]
Mechanical_frequency_MHz= 1.5247568999993746
#Mechanical_frequency_MHz= 1.5247568999993746


Cavity_Resonance_new=[5.096825412,5.096828182]




#%% TXT writer VNA
f_points=VNA.read_f()
S_points=VNA.read_S()




f_points_data_string=f_points.split()
f_points_data=pd.to_numeric(f_points_data_string[1:])

S_points=VNA.read_S()[12:] #remove hash
lines=S_points.split('\n')[:-1]
Sreal=[]
Simag=[]
for line in lines:
    fields=line.split(',')
    Sreal.append(float(fields[0]))
    Simag.append(float(fields[1]))
print(Sreal[:3])
print(Simag[:3])

pf = pd.DataFrame({'Frequency(Hz)':f_points_data, 'RealPower': Sreal, 'ImagPower':Simag})
 # Check the DataFrame (optional step)
print(pf.head())  # This will print the first few rows of the DataFrame
 
pf.to_csv(r'C:\Users\manip.ubt\Rawdata\RawdatapumpPower_-10dB_probe_-10dB_200mK_shiftednew.txt', sep='\t', index=False)
#%% TSV writer FSP
data_points2=FSP.single_trace()

pf = pd.DataFrame(data_points2, columns=['Frequency(Hz)','Magnitude(dBm)'])
  # Check the DataFrame (optional step)
print(pf.head())  # This will print the first few rows of the DataFrame
  
pf.to_csv(r'C:\Users\manip.ubt\Rawdata\analyser_test3.txt', sep='\t', index=False)
# =============================================================================


#%%
# for algebraic calc.
Cavity_Resonance_freq_new=[4.7117,5.0200,5.0987,5.3640,5.8229,5.9739,7.3284,7.8024]  
Cavity_resonance_prev = [4.707,5.015,5.085,5.967,7.324]
equivalence_1=[x/4.707 for x in Cavity_resonance_prev]
equivalence_2= [x/4.7117 for x in Cavity_Resonance_freq_new]
print(equivalence_1) 
print(equivalence_2)    
