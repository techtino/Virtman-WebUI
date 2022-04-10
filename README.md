# VirtMan

Required Dependencies:
* GNU/Linux Distribution
* Python
* Django
* Libvirt
* QEMU
* VMWare
* Virtualbox (With VNC Extension Pack setup)

+ the following python packages:
sudo pip3 install libvirt-python django-ckeditor psutil
Preparing Libvirt:

Add:
~~~
unix_sock_group = "libvirt"
unix_sock_rw_perms = "0770"
~~~

to /etc/libvirt/libvirtd.conf

`sudo virsh net-autostart`
Then:
`sudo systemctl restart libvirtd`



And ensure the user is in the libvirt group.

Running the Django Server:

~~~
python virtman/manage.py flush (reset database)
python virtman/manage.py createsuperuser (create user account)
python virtman/manage.py runserver
~~~

Eventually, a script to prepare the host system will be created
