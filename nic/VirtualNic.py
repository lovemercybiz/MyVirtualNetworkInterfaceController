# -*- coding: utf-8 -*-
import sys
import os
import configparser  # pip install configparser
from threading import Thread, Lock, Semaphore
from winpcapy import WinPcap, WinPcapDevices  # pip install winpcapy
import signal  # monitor Ctrl+C event
import time
import netifaces  # pip install netifaces
from utility.NicCommon import *
from utility.ProtocolCommon import *
from utility.LogCommon import *


NIC_COUNT = 1
SEPERATOR = '-' * 20 + '<按下Ctrl+C退出>' + '-' * 20
IS_VERBOSE = True

VNIC_MAC_BYTES = b''
VNIC_IPV4_INT = 0
NIC_INFO = None
# START_TIME = 0.0


def exit(signum, frame):
    try:
        NIC_INFO.capture.stop()
    except:
        pass
    raise KeyboardInterrupt
    # sys.exit(1)


def packet_callback(win_pcap, param, header, pkt_data):
    # global START_TIME
    try:
        ethernet_ii = EthernetII(pkt_data)
        if(ethernet_ii.is_initialized):
            if(ethernet_ii.dst_mac_bytes == VNIC_MAC_BYTES or ethernet_ii.dst_mac_bytes == b'\xff\xff\xff\xff\xff\xff'):
                if(ethernet_ii.type_int == 0x0806):  # ARP
                    address_resolution_protocol = AddressResolutionProtocol(
                        pkt_data)
                    if(address_resolution_protocol.is_initialized):
                        if(address_resolution_protocol.opcode_int == 1):  # ARP Request
                            if(address_resolution_protocol.target_ip_int == VNIC_IPV4_INT):
                                # modify arp
                                address_resolution_protocol.target_mac_bytes = address_resolution_protocol.sender_mac_bytes
                                address_resolution_protocol.target_ip_int = address_resolution_protocol.sender_ip_int
                                address_resolution_protocol.sender_mac_bytes = VNIC_MAC_BYTES
                                address_resolution_protocol.sender_ip_int = VNIC_IPV4_INT
                                # end modify arp
                                arp_packet = address_resolution_protocol.get_response()
                                ethernet_header = get_ethernet_ii_frame(
                                    ethernet_ii.src_mac_bytes, VNIC_MAC_BYTES, 0x0806)
                                win_pcap.send(ethernet_header + arp_packet)
                elif(ethernet_ii.type_int == 0x0800):  # IPv4
                    internet_protocol_version_4 = InternetProtocolVersion4(
                        pkt_data)
                    if(internet_protocol_version_4.is_initialized):
                        if(internet_protocol_version_4.dst_ip_int == VNIC_IPV4_INT):
                            if(internet_protocol_version_4.protocol_int == 1):  # ICMP
                                internet_control_message_protocol = InternetControlMessageProtocol(
                                    pkt_data)
                                if(internet_control_message_protocol.is_initialized):
                                    # ICMP Echo Request
                                    if(internet_control_message_protocol.type_int == 8 and internet_control_message_protocol.code_int == 0):
                                        icmp_packet = internet_control_message_protocol.get_echo_reply()
                                        tmp_ip_int = internet_protocol_version_4.src_ip_int
                                        internet_protocol_version_4.src_ip_int = internet_protocol_version_4.dst_ip_int
                                        internet_protocol_version_4.dst_ip_int = tmp_ip_int
                                        ip_header = internet_protocol_version_4.get_packet()
                                        ethernet_header = get_ethernet_ii_frame(
                                            ethernet_ii.src_mac_bytes, VNIC_MAC_BYTES, 0x0800)
                                        win_pcap.send(
                                            ethernet_header + ip_header + icmp_packet)
    except Exception as e:
        error_print("Processing frame or packet with {}.".format((e)))


def listen(id, name):
    global NIC_INFO  # , START_TIME
    # START_TIME = time.time()
    registry_name = name.replace(r'\Device\NPF_', '')
    ip, mask = try_get_ip_mask_value_of_nic(registry_name)
    mac = try_get_mac_bytes_of_nic(registry_name)
    gip, gmac = try_get_gateway_of_nic(registry_name)
    with WinPcap(name) as capture:
        NIC_INFO = NicInfo(
            capture, id, ip, mask, mac, 0, gip, gmac)
        debug_print("NIC Info: {}".format((str(NIC_INFO))))
        warning_print(SEPERATOR)
        capture.run(packet_callback)
    warning_print("准备退出关于NIC[{}]的监听子程序...".format((id)))


class VirtualNic:
    def __init__(self, fil):
        self.cfg_path = fil

    def start(self):
        global VNIC_MAC_BYTES, VNIC_IPV4_INT, NIC_INFO

        cfg = configparser.ConfigParser()

        # open config.ini
        cfg.read(self.cfg_path)
        assert cfg.has_option("VirtualNic", "MacAddress")
        vnic_mac_str = cfg.get("VirtualNic", "MacAddress").replace(
            ":", "").replace("-", "")
        assert len(vnic_mac_str) == 12
        VNIC_MAC_BYTES = bytes.fromhex(vnic_mac_str)
        assert cfg.has_option("VirtualNic", "Ipv4Address")
        vnic_ip_str = cfg.get("VirtualNic", "Ipv4Address")
        VNIC_IPV4_INT = get_ip_value(vnic_ip_str)

        # show nic devices
        dev_dict = WinPcapDevices.list_devices()
        info_print("当前配置的网络适配器:".format())
        nic_cnt = len(dev_dict)
        nic_names = list(dev_dict.keys())
        nic_ids = {str(i) for i in range(1, nic_cnt + 1)}
        nic_idx = 0
        for nic_name in nic_names:
            nic_idx += 1
            info_print(
                "NIC[{}] -> name='{}', description='{}'".format((nic_idx), (nic_name), (try_get_nic_device_description(nic_name, dev_dict[nic_name]))))
        nic_names.insert(0, "")

        # choose two nics
        sel_nic_ids = []
        try:
            has_wrong_input = False
            while len(sel_nic_ids) < NIC_COUNT:
                sel_nic = get_striped_input_from_stdin("{}选择第{}块捕获适配器编号({})=>".format((has_wrong_input and '编号非法，请重新' or ''), (1+len(sel_nic_ids)), ('或'.join(nic_ids))))
                if sel_nic in nic_ids:
                    sel_nic_ids.append(int(sel_nic))
                    nic_ids.remove(sel_nic)
                    has_wrong_input = False
                else:
                    has_wrong_input = True
            verbose_print(
                "您已成功选择{}个网络适配器:{}".format((NIC_COUNT), (['NIC[{}]'.format((id)) for id in sel_nic_ids])))
            is_success = True
        except:
            is_success = False
        # warning_print(SEPERATOR)

        if(is_success):
            nic_id = sel_nic_ids[0]
            nic_name = nic_names[nic_id]
            thd = Thread(target=listen, args=(nic_id, nic_name))
            thd.setDaemon(True)
            thd.start()

            signal.signal(signal.SIGINT, exit)
            signal.signal(signal.SIGTERM, exit)

            while True:
                try:
                    if not thd.is_alive():
                        break
                    time.sleep(1e6)
                except KeyboardInterrupt:
                    break
            thd.join()

        warning_print("再见!".format())
