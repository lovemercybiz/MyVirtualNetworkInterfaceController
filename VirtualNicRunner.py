# -*- coding: utf-8 -*-
from nic.VirtualNic import VirtualNic
import os
import sys
if __name__ == "__main__":
    dirname, exename = os.path.split(sys.executable)
    if 'python' in exename.lower():
        dir = os.path.dirname(os.path.realpath(__file__))
    else:
        dir = dirname
    fil = os.path.join(dir, "config.ini")
    nic_instance = VirtualNic(fil)
    nic_instance.start()
