"""
STILL BROKEN; TRANSFER NOT READY YET...
need to fix the other side (java on roborio) to take the dataList
"""

import usb.core
import usb.util

import os

class Transfer(object):

    def __init__(self, port=None):
        self.port = port
        if not port:
            self.dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

    def get_dev(self):

        try:
            output = os.popen("lsusb -D /dev/bus/usb/001/005").read() # find the port that RoboRio is connected to
            # in most cases, the port will be the one above.

            idVendor = hex(int(output.split("idVendor")[1][:17].strip(), base=16))
            idProduct = hex(int(output.split("idProduct")[1][:17].strip(), base=16))

            self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)

            return True
        
        except Exception as e:
            print(f"Exception caused by: {e}")
            return False

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
