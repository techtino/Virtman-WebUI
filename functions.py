import libvirt
import sys

def connectToHypervisor():
    try:
        conn = libvirt.open(None)
    except libvirt.libvirtError:
        print('Failed to open connection to the hypervisor')
        conn = ("Failed")
    return conn

def connectToVM(conn, vm_name):
    try:
        VM = conn.lookupByName(vm_name)
    except libvirt.libvirtError:
        print('Failed to find the main domain')
        
    return VM






vm_name = input("Enter VM Name: ")

conn = connectToHypervisor()
VM = connectToVM(conn, vm_name)
