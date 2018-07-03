import libvirt
import paramiko
from contextlib import contextmanager

class Virt(object):
    ''' Class for manipulation with a virtual machine
    '''

    def __init__(self, connection, name, ip, password):
        self.connection = connection
        self.name = name
        self.ip = ip
        self.virtpass = password

        self.dom = None
        self.snapshot = "vm_test_" + self.name

        auth = [[libvirt.VIR_CRED_AUTHNAME, libvirt.VIR_CRED_PASSPHRASE], self.request_cred, None]
        try:
            conn = libvirt.openAuth(self.connection, auth, 0)
        except libvirt.libvirtError as e:
            raise RuntimeError("Failed to open connection:\n%s", str(e))

        try:
            self.dom = conn.lookupByName(self.name)
        except libvirt.libvirtError:
            raise RuntimeError("Virtual machine %s not found", self.name)

    def request_cred(self, credentials):
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = "root"
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = self.virtpass
        return 0

    @contextmanager
    def ssh_connection(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(self.ip, username="root", password=self.virtpass)
        except paramiko.AuthenticationException:
            raise RuntimeError("Authentication failed while trying to connect to virtual machine.")

        yield ssh

        ssh.close()

    def create_snapshot(self):
        snapshots = self.dom.snapshotListNames()
        if self.snapshot in snapshots:
            try:
                snap = self.dom.snapshotLookupByName(self.snapshot)
                snap.delete()
            except libvirt.libvirtError as e:
                raise RuntimeError("Failed to delete snapshot:\n %s", str(e))

        with self.ssh_connection():
            try:
                snap_xml = "<domainsnapshot><name>%s</name></domainsnapshot>" % self.snapshot
                self.dom.snapshotCreateXML(snap_xml)
            except libvirt.libvirtError as e:
                raise RuntimeError("Failed to create snapshot:\n%s.", str(e))

    def revert_to_snapshot(self):
        try:
            snap = self.dom.snapshotLookupByName(self.snapshot)
            self.dom.revertToSnapshot(snap)
        except libvirt.libvirtError as e:
            raise RuntimeError("Failed to revert to snapshot:\n %s", str(e))

    def remove_snapshot(self):
        try:
            snap = self.dom.snapshotLookupByName(self.snapshot)
            snap.delete()
        except libvirt.libvirtError as e:
            raise RuntimeError("Failed to delete snapshot:\n %s", str(e))

    def start(self):
        if not self.dom.isActive():
            try:
                self.dom.create()
            except libvirt.libvirtError as e:
                raise RuntimeError("Failed to start virtual machine: %s", str(e))

    def stop(self):
        try:
            self.dom.destroy()
        except libvirt.libvirtError as e:
            raise RuntimeError("Failed to stop virtual machine: %s", str(e))

