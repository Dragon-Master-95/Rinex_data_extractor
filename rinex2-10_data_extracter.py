"""
Rinex 2.10 data Extracter code 
version-1.0
Creator: Harsha Avinash Tanti aka Dragon Master

This file extracts the data of Rinex file i.e., Pseudoranges,
SNR/Signal, Doppler etc.

Folowing is the data header format and observations over head:
https://epic.awi.de/id/eprint/51856/1/Gurtner_2007_rinex210.pdf

Thanks to Dr. Werner Gurtner, Astronomical Institute, University of Berne
for description of the Rinex 2.10 format

About code -

The version 1.0 of the code decodes Rinex 2.10 file into 2 parts -
1. Headers
2. Data CSV file containg date, time, 8 data metric and satellite number

This is a crude and barely user friendly code which only gives you the option of 
selecting the Rinex 2.10 file and then it decodes and save data in CSV format bearing the 
same name with added word data/metadata.



NOTE:- This was an interesting project requested by someone. I am willing make imporvement 
to this code according your comments and feedback. Furthermore, If you have these kind of 
interesting projects please let me know, I will code for ya. A little remunarations will be 
required if the project is big.
    
"""

#importing libararies 

import pandas as pd
import numpy as np
from tkinter import *
from tkinter.filedialog import askopenfilename 
from tkinter.filedialog import asksaveasfilename  

file_path = "unassigned"
fname = "unassigned"
my_filetypes = [('All files', '.*'), ('text files', '.txt'), ('CSV files', '.csv')]
name_var = "unassigned"
save_metadata = []
save_data = []


def openfile():
    global file_path
    file_path = askopenfilename()
    root.destroy()


         
def findsats(string):
    #'G': GPS 
    #'R': GLONASS
    #'S': Geostationary signal payload
    #'T': NNSS Transit
    #'M': Mixed
    string = string.strip('\n')
    satn = ['G','R','S','T','M']
    indx = []
    count = 0
    for i in range(0,len(string)):
        if(string[i]==satn[0]):
            indx.append(count)
        if(string[i]==satn[1]):
            indx.append(count)
        if(string[i]==satn[2]):
            indx.append(count)
        if(string[i]==satn[3]):
            indx.append(count)
        if(string[i]==satn[4]):
            indx.append(count)
                
        count = count + 1
    #print(indx)
    #print(string)
    noSat = int(string[0:indx[0]])
    Sats = []
    for i in range(0,len(indx)-1):
        Sats.append(string[indx[i]:indx[i+1]])
    Sats.append(string[indx[i+1]:])
    #print(Sats)
    #print(noSat)
    return noSat, Sats



def extractor(epoch,date_time,event_flag,no_sat_event,sats_event,raw_data,no_obs):
    ext_data = []
    count = -1
    for indx in epoch:
        count = count+1
        arr = np.empty((no_sat_event[count],8),dtype=float)
        arr[:] = np.nan
        i=1
        flag=0
        slack=0
        while((i<2*len(sats_event[count])) & (flag==0)):
            var = indx+i
            
#            print(var)
            if(len(raw_data[var])<6):
                for j in range(0,len(raw_data[var])):
                    try:
                        arr[slack,j]=float(raw_data[var][j])
                    except:
                        g=0
                i=i+1
                var = indx+i
                for j in range(0,len(raw_data[var])):
                    try:
                        arr[slack,j+5]=float(raw_data[var][j])
                    except:
                        g=0
                i=i+1
                var = indx+i
                slack=slack+1
            else:
                flag=1
#        ext_data.append([date_time[count],arr,sats_event[count]])
        for k in range(0,len(sats_event[count])):
            ext_data.append([date_time[count][0],date_time[count][1],date_time[count][2],
                             date_time[count][3],date_time[count][4],date_time[count][5],
                             arr[k,0],arr[k,1],arr[k,2],arr[k,3],arr[k,4],arr[k,5],
                             arr[k,6],arr[k,7],sats_event[count][k]])

    return ext_data


def dataexrtactor(file):
    filepath= file
    with open(filepath,'r') as f:
        lines = f.readlines()
    
    # raw mwta data extraction
    raw_metadata = []
    count = 0;
    for line in lines:
        if(("END" in line) and ("HEADER" in line)):
            print(count)
            break
        raw_metadata.append(line)
        count = count+1
    
    
    #raw data extraction
    raw_data = []
    count2 = 0
    for line in lines:
        if(count2>count):
            temp = line.split(' ')
            temp = [i for i in temp if i]
            raw_data.append(temp)
        count2=count2+1
    
    
    #raw data analysis
    # this has to be done in 2 parts
    # 1. decoding each header before reading data
    # 2. record each reading below it
    count3=-1
    epoch = []
    date_time = []
    event_flag = []
    no_sat_event = []
    sats_event = []
    for i in range(0,len(raw_data)):
        try:
            raw_data[i].remove('\n')
        except:
            go=1 
        if(len(raw_data[i])>5):
            epoch.append(i)
            count3=count3+1
            #for j in range(0,len(raw_data[i])):
            # date are first 6 elements of list in yy mm dd hh mm ss
            # Event/epoch success or failure is given by 7th element
            # the first number of the satellite in that epoch/event/observation
            date_time.append([2000+float(raw_data[i][0]),float(raw_data[i][1]),float(raw_data[i][2]),float(raw_data[i][3]),float(raw_data[i][4]),float(raw_data[i][5])])
            event_flag.append(float(raw_data[i][6]))
            noSat, Sats = findsats(''.join(raw_data[i][7:]))
            no_sat_event.append(noSat)
            sats_event.append(Sats)
            
            #number of obs is 8 but revision should be done to automatically retrive it
    
    no_obs=8
    ext_data_temp = extractor(epoch,date_time,event_flag,no_sat_event,sats_event,raw_data,no_obs)
    col_name = ['Year','Month','Day','Hours','Minutes','Seconds','C1','L1','D1','S1','P2','L2','D2','S2','PRN']
    df = pd.DataFrame(ext_data_temp,columns=col_name)
    ###### metadata processing needto be addedin next version of this code ######
    #metadata = process_metadata(raw_metadata)
    
    return raw_metadata, df



if __name__ == '__main__':

    root = Tk()
    b1 = Button(root, text='File Open', command = openfile)
    b2 = Button(root, text = "Exit", command = root.destroy)
    b1.pack()
    b2.pack()
    mainloop()
    metadata, data = dataexrtactor(file_path)
    print (file_path)
    name = file_path.split('/')[-1]
    data.to_csv(name+'_data.csv')
    with open(name+'_metadata.csv','w') as f:
        for line in metadata:
            f.write(line)
    
