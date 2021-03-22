import libvirt
import os
import sys
from .models import VM, StorageDisk

def createQemuXML(vm_info):
    KB = 1024 * 1024
    storage_device = str(vm_info['storage_disk'])

    #Generate drive ID by isolating the number from form info
    drive_id = ''.join(i for i in storage_device if i.isdigit())
    
    #Getting drive path and name
    # pylint: disable=no-member
    drive_path = StorageDisk.objects.get(id=drive_id).path

    # pylint: disable=no-member
    drive_name = StorageDisk.objects.get(id=drive_id).name

    #Generate XML template for VM
    xml = """<domain type='kvm'>
        <name>{}</name>
        <memory unit='KiB'>{}</memory>
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
        <devices>
                <disk type='file' device='disk'>
                    <source file='{}{}'/>
                    <driver name='qemu' type='qcow2'/>
                    <target dev='vda' bus='virtio'/>
                </disk>
                <disk type="file" device="cdrom">
                    <driver name="qemu" type="raw"/>
                    <source file="/home/techtino/.cache/LibvirtISOs/install.iso"/>
                    <target dev="sda" bus="sata"/>
                    <readonly/>
                    <boot order="1"/>
                    <address type="drive" controller="0" bus="0" target="0" unit="0"/>
                </disk>
                <interface type="network">
                    <source network="default" />
                    <model type='virtio'/>
                </interface>
                  <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
                    <listen type='address' address='0.0.0.0'/>
                  </graphics>
        </devices>
        </domain>""".format(vm_info['name'], int(vm_info['ram']) * KB, vm_info['cpus'], drive_path, drive_name)

    #Write XML to a file
    vm_xml = open("/home/techtino/XMLs/QEMU/{}.xml".format(vm_info['name']),'w+')
    vm_xml.write(xml)

def delXML(vm_name):
    os.remove("/home/techtino/XMLs/QEMU/" + vm_name + ".xml")

def startQemuVM(machine_details):
    conn = libvirt.open('qemu:///system')

    xml_file = open("/home/techtino/XMLs/QEMU/{}.xml".format(machine_details.name))
    xml = xml_file.read()
    xml_file.close()
    conn.createXML(xml)

def handle_uploaded_file(f):
    with open('/home/techtino/.cache/LibvirtISOs/install.iso', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def CreateStorageDrive(disk_info):
    size = str(disk_info['size']) + "G"
    os.system("qemu-img create -f qcow2 {}{} {}".format(disk_info['path'],disk_info['name'],size))

def shutdownVM(name):
    conn = libvirt.open('qemu:///system')
    machine = conn.lookupByName(name)
    machine.destroy()
    conn.close()