# -*- coding: utf-8 -*-
import ctypes
import inspect
import os
from threading import Thread, Lock, Semaphore
import netifaces  # pip install netifaces
from utility.LogCommon import *

INIT_NAT_PARSE_INTERVAL = 3.0
INIT_NAT_PARSE_RETRY_MAX = 2
OS_SYSTEM_MAX_ERR_CNT = 3
CMD_WAIT_SECONDS = 30.0


class TerminableThread(Thread):
    def _async_raise_exc(self, exc_type):
        """raises the given exception type in the context of this thread"""
        tid = ctypes.c_long(self.ident)
        if not inspect.isclass(exc_type):
            raise TypeError("Only types can be raised (not instances)")
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            tid, ctypes.py_object(exc_type))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        if self.is_alive():
            try:
                self._async_raise_exc(SystemExit)
                verbose_print(
                    "call TerminableThread._async_raise_exc succeeded.".format())
            except Exception as e:
                error_print(
                    "call TerminableThread._async_raise_exc with {}.".format((e)))


class NicInfo:
    def __init__(self, winpcap, id, ip, mask, mac, idx, gateway_ip, gateway_mac):
        self.capture = winpcap
        self.id = id
        self.ip = ip
        self.mask = mask
        self.addr_bit_and_mask = ip & mask
        self.mac = mac
        self.index = idx
        self.gateway_ip = gateway_ip
        self.gateway_mac = gateway_mac

    def __str__(self):
        return "id={}, ip={}, mask={}, ".format((self.id), (get_ip_string(self.ip)), (get_ip_string(self.mask))) + "addr_bit_and_mask={}, mac={}, ".format((get_ip_string(self.addr_bit_and_mask)), (get_mac_string(self.mac))) + "gateway_ip={}, gateway_mac={}".format((get_ip_string(self.gateway_ip)), (get_mac_string(self.gateway_mac)))


def get_ip_string(val):
    return '.'.join([str((val >> 24) & 0xff), str((val >> 16) & 0xff), str((val >> 8) & 0xff), str((val) & 0xff)])


def get_mac_string(bytearr):
    return '-'.join(['%02X' % i for i in bytearr])


def get_mac_ip_string(bytearr, val):
    return get_mac_string(bytearr)+":"+get_ip_string(val)


def get_nexthop_string(x):
    if x == None:
        return "-"
    else:
        return get_ip_string(x)


def get_ip_value(text):
    nums = text.strip().split('.')
    assert len(nums) == 4
    for snum in nums:
        for c in snum:
            assert c >= '0' and c <= '9'
    vals = []
    for x in nums:
        v = int(x)
        assert v >= 0 and v <= 255
        vals.append(v)
    return (vals[0] << 24) | (vals[1] << 16) | (vals[2] << 8) | (vals[3])


def get_ip_bytes(text):
    return get_ip_value(text).to_bytes(4, 'big')


def get_ip_hexstring(text):
    return '%08x' % get_ip_value(text)


def try_get_ip_value(text):
    try:
        val = get_ip_value(text)
        return True, val
    except:
        return False, 0


def exec_cmd_callback(cmd, output_lst, lock):
    try:
        with os.popen(cmd) as r:
            text = r.read()
    except:
        text = ''
    output_lst.append(text)
    lock.release()


def exec_cmd(cmd):
    lst = []
    lock = Lock()
    lock.acquire()
    thd = TerminableThread(target=exec_cmd_callback,
                           args=(cmd, lst, lock), daemon=True)
    thd.start()
    retbool = lock.acquire(True, CMD_WAIT_SECONDS)
    if not retbool:
        thd.terminate()
    return retbool and lst[0] or ''


def echo_cmd_callback(cmd, lst, lock):
    retv = os.system(cmd)
    lst.append(retv)
    lock.release()


def echo_cmd(cmd):
    debug_print("Running cmd = `{}`".format((cmd)))
    info_print("cmd output =>".format())
    cnt = 0
    while True:
        lst = []
        lock = Lock()
        lock.acquire()
        thd = TerminableThread(target=echo_cmd_callback,
                               args=(cmd, lst, lock), daemon=True)
        thd.start()
        retbool = lock.acquire(True, CMD_WAIT_SECONDS)
        if not retbool:
            thd.terminate()
        if retbool and lst[0] == 0:
            break
        else:
            cnt += 1
            if cnt >= OS_SYSTEM_MAX_ERR_CNT:
                return 1
    return 0


def get_specific_mac(ip_val):
    ip_str = get_ip_string(ip_val)
    exec_cmd('ping -n 1 {}'.format((ip_str)))
    txt = exec_cmd('arp -a')
    for i in txt.split('\n'):
        i = i.strip()
        if(i == ''):
            continue
        iarr = i.split()
        if(len(iarr) == 3):
            if(iarr[0] == ip_str):
                mac_str = iarr[1].replace(':', '').replace('-', '')
                mac_bytes = bytes.fromhex('000000000000')
                if(len(mac_str) == 12):
                    try:
                        mac_bytes = bytes.fromhex(mac_str)
                    except:
                        pass
                return mac_bytes
    return bytes.fromhex('000000000000')


def try_get_mask_value(text):
    try:
        text = text.strip()
        for c in text:
            assert c >= '0' and c <= '9'
        val = int(text)
        assert val >= 0 and val <= 32
        return True, int('1'*val+'0'*(32-val), 2)
    except:
        return False, 0


def try_get_ip_mask_value(addr, mask):
    is_win, ip_val = try_get_ip_value(addr)
    is_suc, mask_val = try_get_ip_value(mask)
    if is_win and is_suc:
        return ip_val, mask_val
    else:
        return 0, 0


def try_get_ip_mask_value_of_nic(registry_name):
    try:
        d = netifaces.ifaddresses(registry_name)[netifaces.AF_INET][0]
        addr = d['addr']
        mask = d['netmask']
        return try_get_ip_mask_value(addr, mask)
    except:
        return 0, 0


def try_get_ip_mac(ip, mac):
    try:
        is_win, ip_val = try_get_ip_value(ip)
        if is_win:
            mac_bytes = bytes.fromhex(mac)
            assert len(mac_bytes) == 6
            return ip_val, mac_bytes
        else:
            return None
    except:
        return None


def try_get_mac_bytes_of_nic(registry_name):
    try:
        mac_str = netifaces.ifaddresses(registry_name)[
            netifaces.AF_LINK][0]['addr'].replace(':', '')
        return bytes.fromhex(mac_str)
    except:
        return bytes.fromhex('000000000000')


def try_get_nic_device_description(name, default_name):
    # try:
    registry_name = name.replace(r'\Device\NPF_', '')
    txt = exec_cmd(
        '2>nul reg query "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Network\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\{}\\Connection" /v Name'.format((registry_name)))
    for i in txt.split('\n'):
        i = i.strip()
        if(i == ''):
            continue
        if 'Name    REG_SZ' in i:
            i = i.replace('Name    REG_SZ', '').strip()
            return i
    # except:
    #     pass
    return default_name


def try_get_gateway_of_nic(registry_name):
    try:
        gateways = netifaces.gateways()[netifaces.AF_INET]
        for gateway in gateways:
            if gateway[1] == registry_name:
                ip = gateway[0]
                is_win, ip_val = try_get_ip_value(ip)
                if is_win:
                    return ip_val, get_specific_mac(ip_val)
                else:
                    return 0, bytes.fromhex('000000000000')
        return 0, bytes.fromhex('000000000000')
    except:
        return 0, bytes.fromhex('000000000000')


def calc_checksum(bytearr):
    ret = 0
    if (len(bytearr) & 1):
        bytearr += b'\0'
    for i in range(len(bytearr) >> 1):
        idx = i << 1
        ret += (bytearr[idx] << 8) | bytearr[idx + 1]
        if ret > 0xffff:
            ret += 1
            ret &= 0xffff
    return ~ret & 0xffff


def calc_checksum_as_bytes(bytearr):
    return calc_checksum(bytearr).to_bytes(2, 'big')


def calc_checksum_as_hexstring(bytearr):
    return '%04x' % calc_checksum(bytearr)


def convert_endpoint_to_ip_and_port(endpnt_str):
    assert ':' in endpnt_str
    arr = endpnt_str.split(':')
    assert len(arr) == 2
    return (arr[0].strip(), int(arr[1]))


def convert_ip_and_port_to_endpoint(ip_port_tup):
    assert 2 == len(ip_port_tup)
    return "{}:{}".format((ip_port_tup[0]), (ip_port_tup[1]))


def get_input_from_stdin_without_exception(msg):
    question_print(msg, end='')
    try:
        return input()
    except:
        return None


def get_striped_input_from_stdin(msg):
    question_print(msg, end='')
    ret = input()
    if ret is None:
        return None
    else:
        ret = ret.strip()
        return ret and ret or None


def get_striped_input_from_stdin_without_exception(msg):
    ret = get_input_from_stdin_without_exception(msg)
    if ret is None:
        return None
    else:
        ret = ret.strip()
        return ret and ret or None
