import argparse
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from itertools import groupby
import os


def extractStats(data):
    nSamp=data.shape
    print(data)
    print(nSamp)

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

def extractFeatures(data):
    '''
    Given the following data where every row is like this:
    tcp_upload_packets, tcp_upload_bytes, quic_upload_packets, quic_upload_bytes, tcp_download_packets, tcp_download_bytes, quic_download_packets, quic_download_bytes

    This function extracts the following features:
    - Mean and Variance of silence and activity times
    - Ratio between upload and download bytes for TCP and QUIC (separately)
    - Mean, median and standard deviation of total bytes
    - Mean, median and standard deviation of number of packets

    Note: Data shape is (300, 8)
    '''

    # Variance of silence and activity times (needs to be 1D)
    silence_durations, activity_durations = extractSilenceActivity(data[:, 1] + data[:, 5] + data[:, 3] + data[:, 7])

    # Silence statistics
    mean_silence_duration = np.mean(silence_durations) if silence_durations else 0
    variance_silence_duration = np.var(silence_durations) if silence_durations else 0

    # Activity statistics
    mean_activity_duration = np.mean(activity_durations) if activity_durations else 0
    variance_activity_duration = np.var(activity_durations) if activity_durations else 0

    # Ratio between upload and download bytes for TCP and QUIC
    download_sum = data[:, 5] + data[:, 7]
    upload_sum = data[:, 1] + data[:, 3]

    # Avoid division by zero
    tcp_ratio = np.mean(np.divide(
        upload_sum, 
        download_sum, 
        out=np.zeros_like(upload_sum, dtype=np.float64),  # Create float output array
        where=download_sum > 0
    ))

    quic_ratio = np.mean(np.divide(
        download_sum, 
        upload_sum, 
        out=np.zeros_like(download_sum, dtype=np.float64),  # Create float output array
        where=upload_sum > 0
    ))
    # Mean, median and standard deviation of total bytes
    total_bytes = data[:, 1] + data[:, 3] + data[:, 5] + data[:, 7]
    bytes_mean = np.mean(total_bytes)
    bytes_median = np.median(total_bytes)
    bytes_std_dev = np.std(total_bytes)

    # Mean, median and standard deviation of number of packets
    packets = data[:, 0] + data[:, 2] + data[:, 4] + data[:, 6]
    packets_mean = np.mean(packets)
    packets_median = np.median(packets)
    packets_std_dev = np.std(packets)

    features = np.hstack((
        mean_silence_duration, variance_silence_duration,
        mean_activity_duration, variance_activity_duration,
        bytes_std_dev, bytes_mean, bytes_median,
        tcp_ratio, quic_ratio,
        packets_mean, packets_median, packets_std_dev
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
                # OLDER FEATURES: wmFeatures=extractStats(data[iobs*slidingValue:iobs*slidingValue+lengthObsWindow,m])
                wmFeatures=extractFeatures(data[iobs*slidingValue:iobs*slidingValue+lengthObsWindow])
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