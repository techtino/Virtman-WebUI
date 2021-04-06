import libvirt
import os
import sys
import time
from .models import VM, StorageDisk, OpticalDisk
from xml.etree import ElementTree as ET

def createQemuXML(vm_info):

    storage_device = vm_info['storage_disk']

    try:
        optical_path = OpticalDisk.objects.get(name=vm_info['optical_disk']).ISOFile.path
        optical_attached = True
    except:
        optical_attached = False

    try:
        #Getting drive path and name
        drive_path = StorageDisk.objects.get(name=storage_device).path
        drive_name = StorageDisk.objects.get(name=storage_device).name
        drive_attached = True
    except:
        drive_attached = False

    HardDisk = ""
    OpticalDiskDevice = ""
    #Generate XML template for VM
    xmlp1 = """<domain type='kvm'>
        <name>{}</name>
        <memory unit='MiB'>{}</memory>
        <vcpu placement='static'>{}</vcpu>
        <os>
            <type>hvm</type>
        </os>
        <clock offset='utc'/>
        <features>
            <acpi/>
            <apic/>
            <pae/>
        </features>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>restart</on_reboot>
        <on_crash>destroy</on_crash>
        """.format(vm_info['name'], int(vm_info['ram']), vm_info['cpus'])

    if (drive_attached == True):
        HardDisk ="""
        <disk type='file' device='disk'>
            <source file='{}{}'/>
            <driver name='qemu' type='qcow2'/>
            <target dev='vda' bus='virtio'/>
        </disk>
        """.format(drive_path,drive_name)

    if (optical_attached == True):
        OpticalDiskDevice ="""
        <disk type="file" device="cdrom">
        <driver name="qemu" type="raw"/>
        <source file="{}"/>
        <target dev="sda" bus="sata"/>
        <readonly/>
        <boot order="1"/>
        <address type="drive" controller="0" bus="0" target="0" unit="0"/>
        </disk>
        """.format(optical_path)

    Network = """
    <interface type="network">
    <source network="default" />
    <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
    <listen type='address' address='0.0.0.0'/>
    </graphics>
    <video>
      <model type="qxl" ram="65536" vram="65536" vgamem="16384" heads="1" primary="yes"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x02" function="0x0"/>
    </video>
    </devices>
    """
    devices = "<devices>" + HardDisk + OpticalDiskDevice + Network

    xml = xmlp1 + devices + "</domain>"
    #Write XML to a file
    vm_xml = open("/home/techtino/XMLs/QEMU/{}.xml".format(vm_info['name']),'w+')
    vm_xml.write(xml)
    conn = libvirt.open("qemu:///system")

    try:
        machine = conn.lookupByName(vm_info['name'])
        machine.undefine()
    except:
        pass
    conn.defineXML(xml)
    
def createVirtualboxXML(vm_info):

    storage_device = vm_info['storage_disk']

    try:
        optical_path = OpticalDisk.objects.get(name=vm_info['optical_disk']).ISOFile.path
        optical_attached = True
    except:
        optical_attached = False

    try:
        #Getting drive path and name
        drive_path = StorageDisk.objects.get(name=storage_device).path
        drive_name = StorageDisk.objects.get(name=storage_device).name
        drive_attached = True
    except:
        drive_attached = False

    HardDisk = ""
    OpticalDiskDevice = ""

    xmlp1 = """
    <domain type='vbox'>
        <name>{}</name>
        <uuid>4dab22b31d52d8f32516782e98ab3fa0</uuid>
        <memory unit="MiB">{}</memory>
        <vcpu placement="static">{}</vcpu>
       <os>
        <type arch="x86_64">hvm</type>
        <boot dev="fd"/>
        <boot dev="cdrom"/>
        <boot dev="hd"/>
        </os>
        <features>
            <acpi/>
            <apic/>
            <pae/>
        </features>
        <clock offset="localtime"/>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>destroy</on_reboot>
        <on_crash>destroy</on_crash>
        <devices>
        """.format(vm_info['name'],int(vm_info['ram']),vm_info['cpus'])

    if drive_attached == True:
        HardDisk = """
        <disk type='file' device='disk'>
        <source file='{}{}'/>
        <target dev='sda' bus='sata'/>
        <address type="drive" controller="0" bus="0" target="0" unit="0"/>
        </disk>
        """.format(drive_path,drive_name)
    
    if optical_attached == True:
        OpticalDiskDevice = """
        <disk type="file" device="cdrom">
        <source file="{}"/>
        <target dev="sdb" bus="sata"/>
        <address type="drive" controller="0" bus="0" target="0" unit="1"/>
        </disk>
        """.format(optical_path)
    
    xmlp2 = """
        <controller type="sata" index="0"/>
        <interface type='user'>
        <mac address='56:16:3e:5d:c7:9e'/>
        <model type='82540eM'/>
        </interface>
        <graphics type='rdp' autoport='yes' multiUser='yes'/>
        <sound model='sb16'/>
        <hostdev mode='subsystem' type='usb'>
        <source>
            <vendor id='0x1234'/>
            <product id='0xbeef'/>
        </source>
        </hostdev>
        <video>
        <model type="vbox" vram="49152" heads="1">
        <acceleration accel3d="no" accel2d="no"/>
        </model>
        </video>
        <hostdev mode='subsystem' type='usb'>
        <source>
            <vendor id='0x4321'/>
            <product id='0xfeeb'/>
        </source>
        </hostdev>
    </devices>
    </domain>
            """
    xml = xmlp1 + HardDisk + OpticalDiskDevice + xmlp2
    vm_xml = open("/home/techtino/XMLs/QEMU/{}.xml".format(vm_info['name']),'w+')
    vm_xml.write(xml)
    virtualboxcon = libvirt.open("vbox:///session")
    try:
        machine = virtualboxcon.lookupByName(vm_info['name'])
        machine.undefine()
    except:
        pass

    virtualboxcon.defineXML(xml)

def delVM(VirtualMachine):
    hypervisor = VirtualMachine.hypervisor
    if hypervisor == 'QEMU':
        conn = libvirt.open("qemu:///system")
    elif hypervisor == 'Virtualbox':
        conn = libvirt.open("vbox:///session")
    elif hypervisor == 'VMware':
        conn = libvirt.open("qemu:///system")

    machine = conn.lookupByName(VirtualMachine.name)
    machine.undefine()
    os.remove("/home/techtino/XMLs/QEMU/" + VirtualMachine.name + ".xml")

def startQemuVM(machine_details):
    hypervisor = machine_details.hypervisor
    if hypervisor == 'QEMU':
        conn = libvirt.open('qemu:///system')
        machine = conn.lookupByName(machine_details.name)
        machine.create()
    elif hypervisor == 'Virtualbox':
        conn = libvirt.open('vbox:///session')
        os.system("VBoxManage modifyvm " + machine_details.name + " --vrde on")
        os.system("VBoxManage modifyvm " + machine_details.name + " --vrdeproperty VNCPassword=secret")
        os.system("vboxmanage startvm " + machine_details.name + " --type headless")
    elif hypervisor == 'VMWare':
        conn = libvirt.open('qemu:///system')

def CreateStorageDrive(disk_info):
    size = str(disk_info['size']) + "G"
    print(size)
    os.system("qemu-img create -f qcow2 {}{} {}".format(disk_info['path'],disk_info['name'],size))

def stopVM(machine, action):
    name= machine.name
    hypervisor = machine.hypervisor

    if hypervisor == 'QEMU':
        conn = libvirt.open('qemu:///system')
    elif hypervisor == 'Virtualbox':
        conn = libvirt.open('vbox:///session')
    elif hypervisor == 'VMWare':
        conn = libvirt.open('qemu:///system')

    machine = conn.lookupByName(name)
    if (action == "forceoff"):
        machine.destroy()
        VM.objects.filter(name=name).update(state='OFF')
    elif (action == "shutdown"):
        machine.shutdown()
        VM.objects.filter(name=name).update(state='OFF')
    elif (action == "reset"):
        machine.destroy()
        if hypervisor == "Virtualbox":
            os.system("vboxmanage startvm " + name + " --type headless")
        else:
            machine.create()
    conn.close()

def getHostCPUStats():
    conn = libvirt.open(None)
    prev_idle = 0
    prev_total = 0
    for num in range(2):
        cpu_values = conn.getCPUStats(-1,0).values()
        idle = conn.getCPUStats(-1,0)['kernel'] + conn.getCPUStats(-1,0)['user']
        total = sum(cpu_values)
        diff_idle = idle - prev_idle
        diff_total = total - prev_total
        diff_usage = (1000 * (diff_total - diff_idle) / diff_total + 5) / 10
        prev_total = total
        prev_idle = idle
        if num == 0:
            time.sleep(0.01)
        else:
            if diff_usage < 0:
                diff_usage = 0
    cpu_usage = 100 - diff_usage
    return cpu_usage

def getGuestCPUStats(name):
    conn = libvirt.open('qemu:///system')
    machine = conn.lookupByName(name)

    t1 = time.time()
    c1 = int (machine.info()[4])
    time.sleep(0.01)
    t2 = time.time()
    c2 = int (machine.info()[4])
    c_nums = int (machine.info()[3])
    usage = (c2-c1)*100/((t2-t1)*c_nums*1e9)

    return usage

def getDiskStats(name):
    conn = libvirt.open('qemu:///system')
    machine = conn.lookupByName(name)
    #diskStats = machine.blockStats("/home/techtino/Disks/MintDisk.qcow2")
    diskStats = "hello"
    return diskStats

def getMemoryStats(name):
    conn = libvirt.open('qemu:///system')
    machine = conn.lookupByName(name)
    machine.setMemoryStatsPeriod(5)
    memoryStats = machine.memoryStats()
    return memoryStats

def getHostMemoryStats():
    conn = libvirt.open(None)
    mem = conn.getMemoryStats(0)
    return mem

def getVNCPort(machine_details):

    if machine_details.hypervisor == "QEMU":
        conn = libvirt.open("qemu:///system")
    elif machine_details.hypervisor == "Virtualbox":
        conn = libvirt.open("vbox:///session")
    domain = conn.lookupByName(machine_details.name)
    #get the XML description of the VM
    vmXml = domain.XMLDesc(0)
    root = ET.fromstring(vmXml)
    #get the VNC port
    graphics = root.findall('./devices/graphics')
    print(graphics)

    for i in graphics:
        port = i.get('port')

    return port

def createCustomVM(machine_details):
    conn = libvirt.open("qemu:///system")
    conn.defineXML(machine_details)
    
    


