import os
import pyqrcode
from pyqrcode import QRCode

ipaddress = ""

from netifaces import interfaces, ifaddresses, AF_INET
for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    if (ifaceName == "wlan0"):
       ipaddress = ', '.join(addresses)
       print(ipaddress)

qrcodeInput = QRCode("rtmp://"+ipaddress+"/live/stream_input")
qrcodeOutput = QRCode("rtmp://"+ipaddress+"/live/stream_output")

qrcodeInput.png("Input.png", scale=8)
qrcodeOutput.png("Output.png", scale=8)

os.system('sudo /usr/local/nginx/sbin/nginx')
