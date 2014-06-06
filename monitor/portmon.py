from scapy import *

def monitor_ports(target,monitored_ports):
    p=IP(dst=target)/TCP(dport=monitored_ports, flags="S")
    ans,unans=sr(p, timeout=1)
    open_ports = []
    closed_ports = []
    for s,n in ans:
        if s[TCP].dport == r[TCP].sport:
            open_ports.append(str(s[TCP].dport))
        else:
            closed_ports.append(str(s[TCP].dport))