from xml.etree import ElementTree as ET

import sys
import libvirt

conn = libvirt.open()

domain = conn.lookupByName(sys.argv[1])

#get the XML description of the VM
vmXml = domain.XMLDesc(0)
root = ET.fromstring(vmXml)

#get the VNC port
graphics = root.find('./devices/graphics')
port = graphics.get('port')

print (port)
