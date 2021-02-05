# -*- coding: utf-8 -*-
from utility.NicCommon import *
from utility.LogCommon import *


def get_ethernet_ii_frame(dst_mac_bytes, src_mac_bytes, type_int):
    return dst_mac_bytes+src_mac_bytes+type_int.to_bytes(2, 'big')


class EthernetII:
    def __init__(self, pkt_data, begin_pos=0):
        try:
            capacity = begin_pos+14
            if len(pkt_data) < capacity:
                raise ValueError('length = {} < {}'.format((len(pkt_data)), (capacity)))

            end_pos = begin_pos+6
            self.dst_mac_bytes = pkt_data[begin_pos:end_pos]
            begin_pos = end_pos
            end_pos = begin_pos+6
            self.src_mac_bytes = pkt_data[begin_pos:end_pos]
            begin_pos = end_pos
            end_pos = begin_pos+2
            self.type_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')
            self.is_initialized = True
        except Exception as e:
            error_print("Parsing Ethernet II frame with {}.".format((e)))
            self.is_initialized = False


class AddressResolutionProtocol:
    def __init__(self, pkt_data, begin_pos=14):
        try:
            capacity = begin_pos+28
            if len(pkt_data) < capacity:
                raise ValueError('length = {} < {}'.format((len(pkt_data)), (capacity)))

            end_pos = begin_pos+2
            self.hw_type_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')
            begin_pos = end_pos
            end_pos = begin_pos+2
            self.prot_type_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')
            begin_pos = end_pos
            end_pos = begin_pos+1

            self.hw_size_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+1

            self.prot_size_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.opcode_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+self.hw_size_int

            self.sender_mac_bytes = pkt_data[begin_pos:end_pos]

            begin_pos = end_pos
            end_pos = begin_pos+self.prot_size_int

            self.sender_ip_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+self.hw_size_int

            self.target_mac_bytes = pkt_data[begin_pos:end_pos]

            begin_pos = end_pos
            end_pos = begin_pos+self.prot_size_int

            self.target_ip_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')
            verbose_print(
                "ARP({}) -> sender=[{}], target=[{}].".format((self.opcode_int), (get_mac_ip_string(self.sender_mac_bytes, self.sender_ip_int)), (get_mac_ip_string(self.target_mac_bytes, self.target_ip_int))))
            self.is_initialized = True
        except Exception as e:
            error_print(
                "Parsing Address Resolution Protocol packet with {}.".format((e)))
            self.is_initialized = False

    def get_response(self):
        assert self.is_initialized
        assert self.opcode_int == 1
        ret = self.hw_type_int.to_bytes(2, 'big')
        ret += self.prot_type_int.to_bytes(2, 'big')
        ret += self.hw_size_int.to_bytes(1, 'big')
        ret += self.prot_size_int.to_bytes(1, 'big')
        ret += (2).to_bytes(2, 'big')
        ret += self.sender_mac_bytes
        ret += self.sender_ip_int.to_bytes(self.prot_size_int, 'big')
        ret += self.target_mac_bytes
        ret += self.target_ip_int.to_bytes(self.prot_size_int, 'big')
        debug_print(
            "ARP(2) -> sender=[{}], target=[{}].".format((get_mac_ip_string(self.sender_mac_bytes, self.sender_ip_int)), (get_mac_ip_string(self.target_mac_bytes, self.target_ip_int))))

        return ret


class InternetProtocolVersion4:
    def __init__(self, pkt_data, begin_pos=14):
        try:
            capacity = begin_pos+20
            if len(pkt_data) < capacity:
                raise ValueError('length = {} < {}'.format((len(pkt_data)), (capacity)))

            end_pos = begin_pos+1
            self.version_and_header_len_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')
            begin_pos = end_pos
            end_pos = begin_pos+1

            self.diff_svc_field_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.total_len_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.identification_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.flags_and_fragment_offset_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+1

            self.time_to_live_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+1

            self.protocol_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.header_cksum_int = int.from_bytes(pkt_data[begin_pos:end_pos], 'big'
                                                   )

            begin_pos = end_pos
            end_pos = begin_pos+4

            self.src_ip_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+4

            self.dst_ip_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            # info_print(
            #     f"IPv4({self.protocol_int}) -> src={get_ip_string(self.src_ip_int)}, dst={get_ip_string(self.dst_ip_int)}")

            self.is_initialized = True
        except Exception as e:
            error_print(
                "Parsing Internet Protocol Version 4 packet with {}.".format((e)))
            self.is_initialized = False

    def get_packet(self):
        assert self.is_initialized
        ret = self.version_and_header_len_int.to_bytes(1, 'big')
        ret += self.diff_svc_field_int.to_bytes(1, 'big')
        ret += self.total_len_int.to_bytes(2, 'big')
        ret += self.identification_int.to_bytes(2, 'big')
        ret += self.flags_and_fragment_offset_int.to_bytes(2, 'big')
        ret += self.time_to_live_int.to_bytes(1, 'big')
        ret += self.protocol_int.to_bytes(1, 'big')
        ret += b'\0\0'
        ret += self.src_ip_int.to_bytes(4, 'big')
        ret += self.dst_ip_int.to_bytes(4, 'big')

        new_cksum = calc_checksum(ret)

        return ret[:10]+new_cksum.to_bytes(2, 'big')+ret[12:]


class InternetControlMessageProtocol:
    def __init__(self, pkt_data, begin_pos=34):
        try:
            capacity = begin_pos+8
            if len(pkt_data) < capacity:
                raise ValueError('length = {} < {}'.format((len(pkt_data)), (capacity)))

            end_pos = begin_pos+1

            self.type_int = int.from_bytes(pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+1

            self.code_int = int.from_bytes(pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.cksum_int = int.from_bytes(pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.identifier_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos
            end_pos = begin_pos+2

            self.seq_num_int = int.from_bytes(
                pkt_data[begin_pos:end_pos], 'big')

            begin_pos = end_pos

            self.data_bytes = pkt_data[begin_pos:]

            info_print(
                "ICMP({},{}) -> id={}, sn={}, cksum={}".format((self.type_int), (self.code_int), (self.identifier_int), (self.seq_num_int), (self.cksum_int)))
            self.is_initialized = True
        except Exception as e:
            error_print(
                "Parsing Internet Control Message Protocol packet with {}.".format((e)))
            self.is_initialized = False

    def get_echo_reply(self):
        assert self.is_initialized
        assert self.type_int == 8 and self.code_int == 0

        ret = b'\0\0\0\0'
        ret += self.identifier_int.to_bytes(2, 'big')
        ret += self.seq_num_int.to_bytes(2, 'big')
        ret += self.data_bytes
        new_cksum = calc_checksum(ret)

        warning_print(
            "ICMP({},{}) -> id={}, sn={}, cksum={}".format((self.type_int), (self.code_int), (self.identifier_int), (self.seq_num_int), (new_cksum)))
        return b'\0\0' + new_cksum.to_bytes(2, 'big') + ret[4:]
