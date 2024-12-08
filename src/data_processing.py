import argparse
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from itertools import groupby
import os

quartiles = [30, 60, 90]
percentiles = [95, 98]

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
    tcp_upload_packets, tcp_upload_bytes, udp_upload_packets, udp_upload_bytes, tcp_download_packets, tcp_download_bytes, udp_download_packets, udp_download_bytes

    Note: Data shape is (Window Size, Number of Metrics)
    '''

    # Variance of silence and activity times (needs to be 1D)
    silence_durations, activity_durations = extractSilenceActivity(data[:, 0] + data[:, 2] + data[:, 4] + data[:, 6], threshold=2)

    # Silence statistics
    mean_silence_duration = np.mean(silence_durations) if silence_durations else 0
    variance_silence_duration = np.var(silence_durations) if silence_durations else 0

    # Activity statistics
    mean_activity_duration = np.mean(activity_durations) if activity_durations else 0
    variance_activity_duration = np.var(activity_durations) if activity_durations else 0
    quartiles_activity_duration = np.array(np.percentile(activity_durations, quartiles)) if activity_durations else np.zeros(len(quartiles))

    # Mean and Standard deviation of number of bytes (download and upload) for TCP and udp
    tcp_upload_bytes = data[:, 1]
    tcp_download_bytes = data[:, 5] 
    udp_upload_bytes = data[:, 3]
    udp_download_bytes = data[:, 7]

    tcp_upload_bytes_std_dev = np.std(tcp_upload_bytes)
    tcp_download_bytes_std_dev = np.std(tcp_download_bytes)
    udp_upload_bytes_std_dev = np.std(udp_upload_bytes)
    udp_download_bytes_std_dev = np.std(udp_download_bytes)

    tcp_upload_bytes_mean = np.mean(tcp_upload_bytes)
    tcp_download_bytes_mean = np.mean(tcp_download_bytes)
    udp_upload_bytes_mean = np.mean(udp_upload_bytes)
    udp_download_bytes_mean = np.mean(udp_download_bytes)

    # Quartiles of download and upload bytes
    quartiles_upload_bytes = np.array(np.percentile(tcp_upload_bytes + udp_upload_bytes, percentiles))
    quartiles_download_bytes = np.array(np.percentile(tcp_download_bytes + udp_download_bytes, percentiles))
    
    # Mean and standard deviation of total bytes
    total_bytes = data[:, 1] + data[:, 3] + data[:, 5] + data[:, 7]
    bytes_mean = np.mean(total_bytes)
    bytes_std_dev = np.std(total_bytes)

    # Mean and standard deviation of number of packets
    packets = data[:, 0] + data[:, 2] + data[:, 4] + data[:, 6]
    packets_mean = np.mean(packets)
    packets_std_dev = np.std(packets)

    features = np.hstack((
        mean_silence_duration, variance_silence_duration,
        mean_activity_duration, variance_activity_duration, quartiles_activity_duration,
        tcp_upload_bytes_std_dev, tcp_download_bytes_std_dev, udp_upload_bytes_std_dev, udp_download_bytes_std_dev,
        tcp_upload_bytes_mean, tcp_download_bytes_mean, udp_upload_bytes_mean, udp_download_bytes_mean,
        quartiles_upload_bytes, quartiles_download_bytes,
        bytes_mean, bytes_std_dev,
        packets_mean, packets_std_dev
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
        fname=''.join(fileInput.split('.')[:-1])+"_features_m{}_w{}.csv".format(method,lengthObsWindow)
    else:
        fname=''.join(fileInput.split('.')[:-1])+"_features_m{}_w{}_s{}.csv".format(method,lengthObsWindow,slidingValue)
    
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
        columnsNames = ["mean_silence_duration", 
                        "mean_silence_duration", 
                       "variance_silence_duration", 
                       "mean_activity_duration", 
                       "variance_activity_duration", 
                       f"{quartiles[0]}_quartile_activity_duration", 
                       f"{quartiles[1]}_quartile_activity_duration", 
                       f"{quartiles[2]}_quartile_activity_duration",
                       "tcp_upload_bytes_std_dev", 
                       "tcp_download_bytes_std_dev", 
                       "udp_upload_bytes_std_dev", 
                       "udp_download_bytes_std_dev",
                       "tcp_upload_bytes_mean", 
                       "tcp_download_bytes_mean", 
                       "udp_upload_bytes_mean", 
                       "udp_download_bytes_mean",
                       f"{percentiles[0]}_percentile_upload_bytes", 
                       f"{percentiles[1]}_percentile_upload_bytes", 
                       f"{percentiles[0]}_percentile_download_bytes", 
                       f"{percentiles[1]}_percentile_download_bytes",
                       "bytes_mean", 
                       "bytes_std_dev",
                       "packets_mean", 
                       "packets_std_dev"
                       ]
        np.savetxt(fname,features,fmt='%.3f',header="".join(columnsNames))
        # np.savetxt(fname,features,fmt='%.3f')
    else:
        raise ValueError("Method not implemented yet")
            
        

if __name__ == '__main__':
    main()