import argparse
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from itertools import groupby
import os


def extractStats(data):
    nSamp=data.shape
    print(data)

    M1=np.mean(data,axis=0)
    Md1=np.median(data,axis=0)
    Std1=np.std(data,axis=0)
#   p=[75,90,95,98]
#   Pr1=np.array(np.percentile(data,p,axis=0))
    
    features=np.hstack((M1,Md1,Std1))
    return(features)

def extractStatsAdv(data,threshold=0):
    nSamp=data.shape
    print(data)

    M1=np.mean(data,axis=0)
    Md1=np.median(data,axis=0)
    Std1=np.std(data,axis=0)
#   p=[75,90,95,98]
#   Pr1=np.array(np.percentile(data,p,axis=0))

    silence,activity=extractSilenceActivity(data,threshold)
    
    if len(silence)>0:
        silence_faux=np.array([len(silence),np.mean(silence),np.std(silence)])
    else:
        silence_faux=np.zeros(3)
        
    # if len(activity)>0:
        # activity_faux=np.array([len(activity),np.mean(activity),np.std(activity)])
    # else:
        # activity_faux=np.zeros(3)
    # activity_features=np.hstack((activity_features,activity_faux))  
    
    features=np.hstack((M1,Md1,Std1,silence_faux))
    return(features)

def extractSilenceActivity(data,threshold=0):

    # FIXME: combined_data = np.sum(data[:, [0, 2, 4, 6]], axis=1)

    if(data[0]<=threshold):
        s=[1]
        a=[]
    else:
        s=[]
        a=[1]
    for i in range(1,len(data)):
        if(data[i-1]>threshold and data[i]<=threshold):
            s.append(1)
        elif(data[i-1]<=threshold and data[i]>threshold):
            a.append(1)
        elif (data[i-1]<=threshold and data[i]<=threshold):
            s[-1]+=1
        else:
            a[-1]+=1
    return(s,a)

def extractStatsNew(data):
    # Variância dos tempos de silêncio e atividade
    silence_durations, activity_durations = extractSilenceActivity(data)

    # Estatísticas de silêncio
    num_silences = len(silence_durations)
    mean_silence_duration = np.mean(silence_durations) if silence_durations else 0
    variance_silence_duration = np.var(silence_durations) if silence_durations else 0

    # Estatísticas de atividade
    num_activities = len(activity_durations)
    mean_activity_duration = np.mean(activity_durations) if activity_durations else 0
    variance_activity_duration = np.var(activity_durations) if activity_durations else 0

    # Desvio padrão do número de bytes totais
    total_bytes = data[:, 1] + data[:, 5] + data[:, 3] + data[:, 7]
    bytes_std_dev = np.std(total_bytes)

    # Rácio de bytes enviados e recebidos (Upload/Download)
    tcp_upload = data[:, 1]
    tcp_download = data[:, 5]
    quic_upload = data[:, 3]
    quic_download = data[:, 7]
    
    tcp_ratio = np.mean(tcp_upload / tcp_download) if np.any(tcp_download) else np.inf
    quic_ratio = np.mean(quic_upload / quic_download) if np.any(quic_download) else np.inf

    # Estatísticas da janela de observação
    mean_window = np.mean(data, axis=0)
    median_window = np.median(data, axis=0)
    std_dev_window = np.std(data, axis=0)

    # Combina todas as estatísticas em um único vetor
    features = np.hstack((
        num_silences, mean_silence_duration, variance_silence_duration,
        num_activities, mean_activity_duration, variance_activity_duration,
        bytes_std_dev, tcp_ratio, quic_ratio,
        mean_window, median_window, std_dev_window
    ))
    return features

def seqObsWindow(data,lengthObsWindow):
    iobs=0
    nSamples,nMetrics=data.shape
    while iobs*lengthObsWindow<nSamples-lengthObsWindow:
        obsFeatures=np.array([])
        for m in np.arange(nMetrics):
            wmFeatures=extractStats(data[iobs*lengthObsWindow:(iobs+1)*lengthObsWindow,m])
            obsFeatures=np.hstack((obsFeatures,wmFeatures))
        iobs+=1
        
        if 'allFeatures' not in locals():
            allFeatures=obsFeatures.copy()
        else:
            allFeatures=np.vstack((allFeatures,obsFeatures))
    return(allFeatures)

        
def slidingObsWindow(data,lengthObsWindow,slidingValue):
    iobs=0
    nSamples,nMetrics=data.shape
    while iobs*slidingValue<nSamples-lengthObsWindow:
        obsFeatures=np.array([])
        for m in np.arange(nMetrics):
            wmFeatures=extractStats(data[iobs*slidingValue:iobs*slidingValue+lengthObsWindow,m])
            obsFeatures=np.hstack((obsFeatures,wmFeatures))
        iobs+=1
        
        if 'allFeatures' not in locals():
            allFeatures=obsFeatures.copy()
        else:
            allFeatures=np.vstack((allFeatures,obsFeatures))
    return(allFeatures)
        
def slidingMultObsWindow(data,allLengthsObsWindow,slidingValue):
    iobs=0
    nSamples,nMetrics=data.shape
    while iobs*slidingValue<nSamples-max(allLengthsObsWindow):
        obsFeatures=np.array([])
        for lengthObsWindow in allLengthsObsWindow:
            for m in np.arange(nMetrics):
                wmFeatures=extractStats(data[iobs*slidingValue:iobs*slidingValue+lengthObsWindow,m])
                obsFeatures=np.hstack((obsFeatures,wmFeatures))
            iobs+=1
        
        if 'allFeatures' not in locals():
            allFeatures=obsFeatures.copy()
        else:
            allFeatures=np.vstack((allFeatures,obsFeatures))
    return(allFeatures)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('-i', '--input', nargs='?',required=True, help='input file')
    parser.add_argument('-m', '--method', nargs='?',required=False, help='obs. window creation method',default=2)
    parser.add_argument('-w', '--widths', nargs='*',required=False, help='list of observation windows widths',default=60)
    parser.add_argument('-s', '--slide', nargs='?',required=False, help='observation windows slide value',default=0)
    args=parser.parse_args()
    
    fileInput=args.input
    method=int(args.method)
    lengthObsWindow=[int(w) for w in args.widths]
    slidingValue=int(args.slide)
        
    data=np.loadtxt(fileInput,dtype=int)
    if method==1:
        fname=''.join(fileInput.split('.')[:-1])+"_features_m{}_w{}".format(method,lengthObsWindow)
    else:
        fname=''.join(fileInput.split('.')[:-1])+"_features_m{}_w{}_s{}".format(method,lengthObsWindow,slidingValue)
    
    if method==1:
        print("\n\n### SEQUENTIAL Observation Windows with Length {} ###".format(lengthObsWindow[0]))
        features=seqObsWindow(data,lengthObsWindow[0])
        print(features)
        print(fname)
        np.savetxt(fname,features,fmt='%d')
    elif method==2:
        print("\n\n### SLIDING Observation Windows with Length {} and Sliding {} ###".format(lengthObsWindow[0],slidingValue))
        features=slidingObsWindow(data,lengthObsWindow[0],slidingValue)
        print(features)
        print(fname)
        np.savetxt(fname,features,fmt='%d')
    elif method==3:
        print("\n\n### SLIDING Observation Windows with Lengths {} and Sliding {} ###".format(lengthObsWindow,slidingValue))    
        features=slidingMultObsWindow(data,lengthObsWindow,slidingValue)
        print(features)
        print(fname)
        np.savetxt(fname,features,fmt='%d')
    else:
        raise ValueError("Method not implemented yet")
            
        

if __name__ == '__main__':
    main()