import sys
import argparse
import datetime
from netaddr import IPNetwork, IPAddress, IPSet
import pyshark

def pktHandler(timestamp, srcIP, dstIP, lengthIP, protocol, sampDelta, outfile):
    global scnets
    global ssnets
    global npkts
    global T0
    global outc
    global last_ks
    
    if (IPAddress(srcIP) in scnets and IPAddress(dstIP) in ssnets) or (IPAddress(srcIP) in ssnets and IPAddress(dstIP) in scnets):
        if npkts == 0:
            T0 = float(timestamp)
            last_ks = 0
            
        ks = int((float(timestamp) - T0) / sampDelta)
        
        if ks > last_ks:
            outfile.write('{} {} {} {} {} {} {} {}\n'.format(*outc))
            print('{} {} {} {} {} {} {} {}'.format(*outc))
            outc = [0, 0, 0, 0, 0, 0, 0, 0]
            
        if ks > last_ks + 1:
            for j in range(last_ks + 1, ks):
                outfile.write('{} {} {} {} {} {} {} {}\n'.format(*outc))
                print('{} {} {} {} {} {} {} {}'.format(*outc))
        
        if IPAddress(srcIP) in scnets:  # Upload
            if protocol == "TCP":
                outc[0] += 1  # TCP upload packet count
                outc[1] += int(lengthIP)  # TCP upload data size
            elif protocol == "UDP":
                outc[2] += 1  # UDP upload packet count
                outc[3] += int(lengthIP)  # UDP upload data size

        if IPAddress(dstIP) in scnets:  # Download
            if protocol == "TCP":
                outc[4] += 1  # TCP download packet count
                outc[5] += int(lengthIP)  # TCP download data size
            elif protocol == "UDP":
                outc[6] += 1  # UDP download packet count
                outc[7] += int(lengthIP)  # UDP download data size
        
        last_ks = ks
        npkts += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', nargs='?', required=True, help='input file')
    parser.add_argument('-o', '--output', nargs='?', required=False, help='output file')
    parser.add_argument('-f', '--format', nargs='?', required=True, help='format', default=1)
    parser.add_argument('-d', '--delta', nargs='?', required=False, help='sampling delta interval')
    parser.add_argument('-c', '--cnet', nargs='+', required=True, help='client network(s)')
    parser.add_argument('-s', '--snet', nargs='+', required=True, help='service network(s)')
    
    args = parser.parse_args()
    
    if args.delta is None:
        sampDelta = 1
    else:
        sampDelta = float(args.delta)
    
    cnets = []
    for n in args.cnet:
        try:
            nn = IPNetwork(n)
            cnets.append(nn)
        except:
            print('{} is not a network prefix'.format(n))
    if len(cnets) == 0:
        print("No valid client network prefixes.")
        sys.exit()
    global scnets
    scnets = IPSet(cnets)

    snets = []
    for n in args.snet:
        try:
            nn = IPNetwork(n)
            snets.append(nn)
        except:
            print('{} is not a network prefix'.format(n))
    if len(snets) == 0:
        print("No valid service network prefixes.")
        sys.exit()
        
    global ssnets
    ssnets = IPSet(snets)
        
    fileInput = args.input
    fileFormat = int(args.format)
    
    if args.output is None:
        fileOutput = fileInput + "_d" + str(sampDelta) + ".dat"
    else:
        fileOutput = args.output
        
    global npkts
    global T0
    global outc
    global last_ks

    npkts = 0
    outc = [0, 0, 0, 0, 0, 0, 0, 0]  # Separate counters for TCP and UDP
    outfile = open(fileOutput, 'w') 

    if fileFormat in [1, 2]:
        infile = open(fileInput, 'r') 
        for line in infile: 
            pktData = line.split()
            if fileFormat == 1 and len(pktData) == 10:  # script format with protocol
                timestamp, srcIP, dstIP, lengthIP, protocol = pktData[0], pktData[4], pktData[6], pktData[8], pktData[9]
                pktHandler(timestamp, srcIP, dstIP, lengthIP, protocol, sampDelta, outfile)
            elif fileFormat == 2 and len(pktData) == 5:  # tshark format with protocol
                timestamp, srcIP, dstIP, lengthIP, protocol = pktData[0], pktData[1], pktData[2], pktData[3], pktData[4]
                pktHandler(timestamp, srcIP, dstIP, lengthIP, protocol, sampDelta, outfile)
        infile.close()
    elif fileFormat == 3:  # pcap format
        capture = pyshark.FileCapture(fileInput, display_filter='ip')
        for pkt in capture:
            timestamp, srcIP, dstIP, lengthIP, protocol = pkt.sniff_timestamp, pkt.ip.src, pkt.ip.dst, pkt.ip.len, pkt.transport_layer
            pktHandler(timestamp, srcIP, dstIP, lengthIP, protocol, sampDelta, outfile)
    
    outfile.close()


if __name__ == '__main__':
    main()