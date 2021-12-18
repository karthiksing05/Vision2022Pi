"""
STILL BROKEN; TRANSFER NOT READY YET...
need to fix the other side (java on roborio) to take the dataList
"""

import usb.core
import usb.util

class Transfer(object):

    def __init__(self, port=None):
        self.port = port
        if not port:
            self.dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

    def send(self, data) -> bool:
        for config in self.dev:
            config.set()
            for intf in config:
                for ep in intf:
                    if ep.bEndpointAddress:
                        self.dev.write(ep.bEndpointAddress, data, intf.bInterfaceNumber)
                        return True
        else:
            return False
