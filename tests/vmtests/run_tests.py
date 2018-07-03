import re
import os
import time
import sys
import util
from virtman import Virt

connection = "qemu+tcp://root@10.37.176.1/system"
password = "anaconda"

HOSTS_FILE = "hosts"

PATH_PREFIX = "tests/"
TESTS = ["test.yml"]

def get_tests(path = "."):

    all_files = os.listdir(path)
    tests = []
    test_regex = re.compile(r".*test.*\.yml$")

    for file_item in all_files:
        if os.path.isfile(os.path.join(path, file_item)):
            m = test_regex.match(file_item)
            if m:
                tests.append(file_item)
    return tests


def get_hosts(hosts_path, subgroup):

    result = []
    sg_regex = re.compile(r"\[(.*)\]")

    add = False

    with open(hosts_path, "r") as hosts:
        line = hosts.readline()
        while line != '':
            if line.strip() != "":
                m = sg_regex.match(line)
                if m:
                    add = False
                    if m.group(1) == subgroup:
                        add = True
                elif add:
                    result.append(line.strip())
            line = hosts.readline()

    return result


def run_tests(tests):

    result = 0
    host_ips = get_hosts(HOSTS_FILE, 'all')

    vms = []
    for ip in host_ips:
        # VM always have IP address as its name
        vm = Virt(connection, ip, ip, password)
        vms.append(vm)
        vm.start()

    time.sleep(120)

    for vm in vms:
        vm.create_snapshot()

    for test in tests:

        path = "%s%s" % (PATH_PREFIX, test)
        stdout, stderr, code = util.run_command(["ansible-playbook", "-i", HOSTS_FILE, path])

        print("Running '%s':" % test)

        if "fatal" in stdout:
            result = 1
            for line in stdout.splitlines():
                print(line)
            for line in stderr.splitlines():
                print(line)

        for vm in vms:
            vm.revert_to_snapshot()

    for vm in vms:
        vm.remove_snapshot()
        vm.stop()

    return result

def main():
    tests = get_tests()
    ret = run_tests(tests)
    sys.exit(ret)

if __name__ == "__main__":
    main()

