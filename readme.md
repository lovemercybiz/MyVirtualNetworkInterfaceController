# MyVirtualNetworkInterfaceController
A Software-Like NIC Capable of Simulating An NIC Hardware

## Prerequisites
- WinPcap v4.1.3 ***YES AND INSTALL IT***
- WinPcap other than WinPcap v4.1.3 ***NO AND UNINSTALL IT***
- Win10Pcap ***NO AND UNINSTALL IT***
- Npcap ***NO AND UNINSTALL IT***

## How to Run
- ### Windows NT (x86)
```bat
cd dist
REM modify `config.ini` to match your NIC(s).
myvirtualnic_nt32
```
- ### Windows NT (AMD64)
```bat
cd dist
REM modify `config.ini` to match your NIC(s).
myvirtualnic_nt64
```

## How when Running
- ### Windows NT
```console
Info: 当前配置的网络适配器:
Info: NIC[1] -> name='\Device\NPF_{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}', description='以太网'
Info: NIC[2] -> name='\Device\NPF_{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}', description='VMware Network Adapter VMnet8'
Question: 选择第1块捕获适配器编号(2或1)=>1
Verbose: 您已成功选择1个网络适配器:['NIC[1]']
Debug: NIC Info: id=1, ip=192.168.0.2, mask=255.255.255.0, addr_bit_and_mask=192.168.0.0, mac=XX-XX-XX-XX-XX-XX, gateway_ip=192.168.0.1, gateway_mac=XX-XX-XX-XX-XX-XX
Warning: --------------------<按下Ctrl+C退出>--------------------
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.2], target=[00-00-00-00-00-00:192.168.0.222].
Debug: ARP(2) -> sender=[66-55-44-33-22-11:192.168.0.222], target=[XX-XX-XX-XX-XX-XX:192.168.0.2].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Info: ICMP(8,0) -> id=1, sn=66, cksum=19737
Warning: ICMP(8,0) -> id=1, sn=66, cksum=21785
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Info: ICMP(8,0) -> id=1, sn=67, cksum=19736
Warning: ICMP(8,0) -> id=1, sn=67, cksum=21784
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.213].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.214].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.215].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.216].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.217].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.218].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.219].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.220].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.221].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.222].
Debug: ARP(2) -> sender=[66-55-44-33-22-11:192.168.0.222], target=[XX-XX-XX-XX-XX-XX:192.168.0.1].
Info: ICMP(8,0) -> id=1, sn=68, cksum=19735
Warning: ICMP(8,0) -> id=1, sn=68, cksum=21783
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Info: ICMP(8,0) -> id=1, sn=69, cksum=19734
Warning: ICMP(8,0) -> id=1, sn=69, cksum=21782
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Verbose: ARP(1) -> sender=[XX-XX-XX-XX-XX-XX:192.168.0.1], target=[FF-FF-FF-FF-FF-FF:192.168.0.1].
Warning: 准备退出关于NIC[1]的监听子程序...
Warning: 再见!
```
