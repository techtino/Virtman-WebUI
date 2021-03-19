import libvirt
import sys
from .models import VM

def createQemuVM(name, cpus, ram, drivePath, driveName):
    KB = 1024 * 1024
    MB = 1024 * KB
    params = {}
    params['ram'] = ram
    params['vcpu'] = cpus
    params['name'] = name
    params['drivePath'] = drivePath
    params['driveName'] = driveName
    conn = libvirt.open("qemu:///system")
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
        </domain>""".format(params['name'], int(params['ram']) * KB, params['vcpu'], params['drivePath'], params['driveName'])
    conn.createXML(xml)
    conn.close()

def handle_uploaded_file(f):
    with open('/home/techtino/.cache/LibvirtISOs/install.iso', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def CreateStorageDrive():
    conn = libvirt.open('qemu:///system')
    path = "/var/libvirt/images"
    params = {}
    params['path'] = path

    xml = """<pool type="dir">
	<name>vdisk</name>
	<target>
          <path>{}</path>
	</target>
    </pool>""".format(params['path'])

def shutdownVM(name):
    conn = libvirt.open('qemu:///system')
    machine = conn.lookupByName(name)
    machine.destroy()
    conn.close()