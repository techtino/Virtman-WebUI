import libvirt
import os
import shutil
import sys
import time
from .models import VM, StorageDisk, OpticalDisk
from xml.etree import ElementTree as ET

def createQemuXML(vm_info):
    # similar to vbox function, no need to comment again

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
    conn = libvirt.open("qemu:///system")

    try:
        machine = conn.lookupByName(vm_info['name'])
        machine.undefine()
    except:
        pass
    conn.defineXML(xml)
    conn.close()
    
def createVirtualboxXML(vm_info):

    storage_device = vm_info['storage_disk']

    # check if optical disk was chosen and sets true or false
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

    # produce xml template specific to vbox with variables inputted with .format
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

    # add disk drive to xml spec if selected in form
    if drive_attached == True:
        HardDisk = """
        <disk type='file' device='disk'>
        <source file='{}{}'/>
        <target dev='sda' bus='sata'/>
        <address type="drive" controller="0" bus="0" target="0" unit="0"/>
        </disk>
        """.format(drive_path,drive_name)
    
    # add optical disk to spec if selected in form
    if optical_attached == True:
        OpticalDiskDevice = """
        <disk type="file" device="cdrom">
        <source file="{}"/>
        <target dev="sdb" bus="sata"/>
        <address type="drive" controller="0" bus="0" target="0" unit="1"/>
        </disk>
        """.format(optical_path)
    
    # second part of xml, configure rest of components such as controllers, vnc and video
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

    # combine all required parts of XML
    xml = xmlp1 + HardDisk + OpticalDiskDevice + xmlp2

    # connects to virtualbox with libvirt, checks if exists already, then creates a new one
    virtualboxcon = libvirt.open("vbox:///session")
    try:
        machine = virtualboxcon.lookupByName(vm_info['name'])
        machine.undefine()
    except:
        pass

    virtualboxcon.defineXML(xml)
    virtualboxcon.close()

def createVMWareXML(vm_info):
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

    vmxTemplate = """
    #!/usr/bin/vmware
    .encoding = "UTF-8"
    config.version = "8"
    virtualHW.version = "18"
    mks.enable3d = "TRUE"
    pciBridge0.present = "TRUE"
    pciBridge4.present = "TRUE"
    pciBridge4.virtualDev = "pcieRootPort"
    pciBridge4.functions = "8"
    pciBridge5.present = "TRUE"
    pciBridge5.virtualDev = "pcieRootPort"
    pciBridge5.functions = "8"
    pciBridge6.present = "TRUE"
    pciBridge6.virtualDev = "pcieRootPort"
    pciBridge6.functions = "8"
    pciBridge7.present = "TRUE"
    pciBridge7.virtualDev = "pcieRootPort"
    pciBridge7.functions = "8"
    vmci0.present = "TRUE"
    hpet0.present = "TRUE"
    nvram = "{}.nvram"
    virtualHW.productCompatibility = "hosted"
    powerType.powerOff = "soft"
    powerType.powerOn = "soft"
    powerType.suspend = "soft"
    powerType.reset = "soft"
    displayName = "{}"
    usb.vbluetooth.startConnected = "TRUE"
    firmware = "efi"
    sensor.location = "pass-through"
    guestOS = "windows9-64"
    tools.syncTime = "FALSE"
    sound.autoDetect = "TRUE"
    sound.virtualDev = "hdaudio"
    sound.fileName = "-1"
    sound.present = "TRUE"
    numvcpus = "{}"
    cpuid.coresPerSocket = "2"
    memsize = "{}"
    mem.hotadd = "TRUE"
    sata0.present = "TRUE"
    nvme0.present = "TRUE"
    nvme0:0.present = "TRUE"
    sata0:1.deviceType = "cdrom-image"
    usb.present = "TRUE"
    ehci.present = "TRUE"
    usb_xhci.present = "TRUE"
    svga.graphicsMemoryKB = "8388608"
    ethernet0.connectionType = "nat"
    ethernet0.addressType = "generated"
    ethernet0.virtualDev = "e1000e"
    serial0.fileType = "device"
    serial0.fileName = "thinprint"
    ethernet0.present = "TRUE"
    serial0.present = "TRUE"
    extendedConfigFile = "Windows 10 x64.vmxf"
    floppy0.present = "FALSE"
    numa.autosize.cookie = "20022"
    numa.autosize.vcpu.maxPerVirtualNode = "2"
    uuid.bios = "56 4d 22 c7 04 0d 9e 93-63 4c 77 26 24 c7 63 f5"
    uuid.location = "56 4d 22 c7 04 0d 9e 93-63 4c 77 26 24 c7 63 f5"
    vm.genid = "2977167825520945118"
    vm.genidX = "1511474261418836335"
    nvme0:0.redo = ""
    pciBridge0.pciSlotNumber = "17"
    pciBridge4.pciSlotNumber = "21"
    pciBridge5.pciSlotNumber = "22"
    pciBridge6.pciSlotNumber = "23"
    pciBridge7.pciSlotNumber = "24"
    usb.pciSlotNumber = "32"
    ethernet0.pciSlotNumber = "160"
    sound.pciSlotNumber = "33"
    ehci.pciSlotNumber = "34"
    usb_xhci.pciSlotNumber = "192"
    vmci0.pciSlotNumber = "35"
    sata0.pciSlotNumber = "36"
    nvme0.pciSlotNumber = "224"
    svga.vramSize = "268435456"
    vmotion.checkpointFBSize = "134217728"
    vmotion.checkpointSVGAPrimarySize = "268435456"
    vmotion.svga.mobMaxSize = "1073741824"
    vmotion.svga.graphicsMemoryKB = "8388608"
    vmotion.svga.supports3D = "0"
    vmotion.svga.baseCapsLevel = "0"
    vmotion.svga.maxPointSize = "0"
    vmotion.svga.maxTextureSize = "0"
    vmotion.svga.maxVolumeExtent = "0"
    vmotion.svga.maxTextureAnisotropy = "0"
    vmotion.svga.lineStipple = "0"
    vmotion.svga.dxMaxConstantBuffers = "0"
    vmotion.svga.dxProvokingVertex = "0"
    vmotion.svga.sm41 = "0"
    vmotion.svga.multisample2x = "0"
    vmotion.svga.multisample4x = "0"
    vmotion.svga.msFullQuality = "0"
    vmotion.svga.logicOps = "0"
    vmotion.svga.bc67 = "0"
    vmotion.svga.sm5 = "0"
    vmotion.svga.multisample8x = "0"
    vmotion.svga.logicBlendOps = "0"
    ethernet0.generatedAddress = "00:0c:29:c7:63:f5"
    ethernet0.generatedAddressOffset = "0"
    vmci0.id = "617047029"
    monitor.phys_bits_used = "45"
    cleanShutdown = "TRUE"
    softPowerOff = "FALSE"
    usb:1.speed = "2"
    usb:1.present = "TRUE"
    usb:1.deviceType = "hub"
    usb:1.port = "1"
    usb:1.parent = "-1"
    usb_xhci:4.present = "TRUE"
    usb_xhci:4.deviceType = "hid"
    usb_xhci:4.port = "4"
    usb_xhci:4.parent = "-1"
    RemoteDisplay.vnc.enabled = "TRUE"
    RemoteDisplay.vnc.port = "7000"

    """.format(vm_info['name'],vm_info['name'],vm_info['cpus'],vm_info['ram'])

    if drive_attached == True:
        vmxTemplate = vmxTemplate + "nvme0:0.fileName = " + drive_path + "/" + drive_name

    if optical_attached == True:
        vmxTemplate = vmxTemplate + '\nsata0:1.present = "TRUE"' + "\nsata0:1.fileName = " + optical_path

    home = os.path.expanduser("~")
    vmxPath = home + "/vmware/" + vm_info['name'] + "/"
    os.makedirs(vmxPath)

    vmxFile = open (vmxPath + vm_info['name'] + ".vmx", "w+")
    vmxFile.write(vmxTemplate)
    vmxFile.close()

def createLXCXML(container_info):
    xml = """
    <domain type="lxc">
    <name>{}</name>
    <memory unit="MiB">{}</memory>
    <vcpu placement="static">{}</vcpu>
    <os>
        <type arch="x86_64">exe</type>
        <init>{}</init>
    </os>
    <clock offset="utc"/>
    <on_poweroff>destroy</on_poweroff>
    <on_reboot>restart</on_reboot>
    <on_crash>destroy</on_crash>
    <devices>
        <emulator>/usr/lib/libvirt/libvirt_lxc</emulator>
        <interface type="bridge">
        <mac address="00:16:3e:bc:af:f7"/>
        <source bridge="br0"/>
        </interface>
        <console type="pty">
        <target type="lxc" port="0"/>
        </console>
    </devices>
    </domain>
    """.format(container_info['name'],container_info['ram'],container_info['cpus'],container_info['app'])

    conn = libvirt.open("lxc:///system")
    conn.defineXML(xml)

def delVM(VirtualMachine):
    
    # depending on hypervisor type, connect and delete from libvirt, or in case of VMWare delete directory
    try:
        hypervisor = VirtualMachine.hypervisor
        if hypervisor == 'QEMU':
            conn = libvirt.open("qemu:///system")
            machine = conn.lookupByName(VirtualMachine.name)
            machine.undefine()
            conn.close()
        elif hypervisor == 'Virtualbox':
            conn = libvirt.open("vbox:///session")
            machine = conn.lookupByName(VirtualMachine.name)
            machine.undefine()
            conn.close()
        elif hypervisor == 'VMWare':
            home = os.path.expanduser("~")
            shutil.rmtree(home + "/vmware/" + VirtualMachine.name)
    # If machine does not have hypervisor info assume its LXC and delete
    except:
        conn = libvirt.open("lxc:///system")
        machine = conn.lookupByName(VirtualMachine.name)
        machine.undefine()
        conn.close()

def startVM(machine_details):
    hypervisor = machine_details.hypervisor
    # based on hypervisor, run different command to start, as virtualbox does not support libvirt API starting due to bug, and vmware does not either
    if hypervisor == 'QEMU':
        conn = libvirt.open('qemu:///system')
        machine = conn.lookupByName(machine_details.name)
        machine.create()
    # utilise vbox command line to enable vnc and start vm
    elif hypervisor == 'Virtualbox':
        os.system("VBoxManage modifyvm " + machine_details.name + " --vrde on")
        os.system("VBoxManage modifyvm " + machine_details.name + " --vrdeproperty VNCPassword=secret")
        os.system("vboxmanage startvm " + machine_details.name + " --type headless")
    # start vm by pointing to vmx file
    elif hypervisor == 'VMWare':
        home = os.path.expanduser("~")
        os.system("vmrun start " + home + "/vmware/" + machine_details.name + "/" + machine_details.name + ".vmx" + " nogui")
    # If hypervisor is not found, assume LXC
    elif hypervisor == "lxc":
        conn = libvirt.open("lxc:///system")
        machine = conn.lookupByName(machine_details.name)
        machine.create()

def CreateStorageDrive(disk_info):
    size = str(disk_info['size']) + "G"
    if disk_info['type'] == "qcow2":
        os.system("qemu-img create -f qcow2 {}{} {}".format(disk_info['path'],disk_info['name'],size))
    else:
        os.system("qemu-img create -f vmdk {}{} {}".format(disk_info['path'],disk_info['name'],size))

def stopVM(machine, action):
    # gets name and hypervisor from model
    name= machine.name
    hypervisor = machine.hypervisor

    # depending on hypervisor, perform different action/connection.
    if hypervisor == 'QEMU':
        conn = libvirt.open('qemu:///system')
    elif hypervisor == 'Virtualbox':
        conn = libvirt.open('vbox:///session')

    # vmware is stopped and restarted manually due to lack of libvirt API support
    elif hypervisor == 'VMWare':
        home = os.path.expanduser("~")
        # depending on action specified by user button perform different vmrun command
        if (action == "forceoff"):
            os.system("vmrun stop " + home + "/vmware/" + name + "/" + name + ".vmx" + " hard")
            return
        elif (action == "restart"):
            os.system("vmrun reset " + home + "/vmware/" + name + "/" + name + ".vmx")
            return
        elif (action == "shutdown"):
            os.system("vmrun stop " + home + "/vmware/" + name + "/" + name + ".vmx" + " soft")
            return
    elif hypervisor == 'lxc':
        conn = libvirt.open("lxc:///system")

    # looks up vm in API
    machine = conn.lookupByName(name)
    if (action == "forceoff"):
        # destroys vm (hard shutdown)
        machine.destroy()
        # attempt to set vm state (if is lxc container then it wont)
        try:
            VM.objects.filter(name=name).update(state='OFF')
        except:
            pass
    elif (action == "shutdown"):
        # send ACPI shutdown signal, shutdown, restart gui appears in vm
        machine.shutdown()
        VM.objects.filter(name=name).update(state='OFF')
    elif (action == "reset"):
        # destroys vm and starts it again
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
    conn.close()
    return cpu_usage

def getGuestCPUStats(machine):
    if machine.hypervisor == "QEMU":
        conn = libvirt.open("qemu:///system")
    elif machine.hypervisor == 'Virtualbox':
        conn = libvirt.open("vbox:///session")
    elif machine.hypervisor == "VMWare":
        return "No stats available"
    machine = conn.lookupByName(machine.name)

    # algorithm to calculate cpu usage from cpu_time

    # sample first cpu time
    t1 = time.time()
    c1 = int (machine.info()[4])
    time.sleep(0.01)

    # sample second cpu time (get values from machine info)
    t2 = time.time()
    c2 = int (machine.info()[4])
    c_nums = int (machine.info()[3])

    # calculate the usage difference between the two times
    usage = (c2-c1)*100/((t2-t1)*c_nums*1e9)
    conn.close()
    return usage

def getDiskStats(machine):
    
    # connect to hypervisor and get disk stats based for disk image file
    if machine.hypervisor == "QEMU":
        conn = libvirt.open("qemu:///system")
    elif machine.hypervisor == 'Virtualbox':
        return "No stats available for hypervisor"
    elif machine.hypervisor == "VMWare":
        return "No stats available for hypervisor"
    machine = conn.lookupByName(machine.name)
    diskStats = machine.blockStats("/home/techtino/Disks/MintDisk.qcow2")
    conn.close()
    return diskStats

def getMemoryStats(machine):
    
    # connect based on hypervisor type, if unsupported, return 0 to the user
    if machine.hypervisor == "QEMU":
        conn = libvirt.open("qemu:///system")
    elif machine.hypervisor == 'Virtualbox':
        conn = libvirt.open("vbox:///session")
        return 0
    elif machine.hypervisor == "VMWare":
        return 0

    # lookup virtual machine in API
    machine = conn.lookupByName(machine.name)

    # get memory statistics via API
    machine.setMemoryStatsPeriod(5)
    memoryStats = machine.memoryStats()
    conn.close()
    return memoryStats

def getHostMemoryStats():
    
    # Use libvirt to get memory stats and return information to listing
    conn = libvirt.open(None)
    mem = conn.getMemoryStats(0)
    conn.close()
    return mem

def getVNCPort(machine_details):

    # connect to different URL based on hypervisor from machine model
    if machine_details.hypervisor == "QEMU":
        conn = libvirt.open("qemu:///system")
    elif machine_details.hypervisor == "Virtualbox":
        conn = libvirt.open("vbox:///session")

    # no need to connect to libvirt for vmware as using vmrun
    elif machine_details.hypervisor == "VMWare":
        port = "7000"
        return port


    domain = conn.lookupByName(machine_details.name)
    #get the XML description of the VM
    vmXml = domain.XMLDesc(0)
    root = ET.fromstring(vmXml)
    #get the VNC port
    graphics = root.findall('./devices/graphics')

    # loop over all possible to ensure correct port (correct value is at the end)
    for i in graphics:
        port = i.get('port')
    conn.close()
    return port

def createCustomVM(machine_details):
    conn = libvirt.open(None)
    # creates VM from XML
    conn.defineXML(machine_details)

def delDisk(Disk):
    os.remove(Disk.path + Disk.name)
