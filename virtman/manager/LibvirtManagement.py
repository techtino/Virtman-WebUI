import libvirt
import sys

def createQemuVM():
    KB = 1024 * 1024
    MB = 1024 * KB
    params = {}
    params['ram'] = 1
    params['vcpu'] = 1
    params['name'] = "windows"
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
                    <source file='/var/lib/libvirt/images/win10.qcow2'/>
                    <driver name='qemu' type='qcow2'/>
                    <target dev='vda' bus='virtio'/>
                </disk>
                <interface type="network">
                    <source network="default" />
                    <model type='virtio'/>
                </interface>
                  <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
                    <listen type='address' address='0.0.0.0'/>
                  </graphics>
        </devices>
        </domain>""".format(params['name'], int(params['ram']) * KB, params['vcpu'])
    conn.createXML(xml)

#createQemuVM()