#!/usr/bin/python

import glob
import os

from ansible.module_utils.basic import AnsibleModule


SEARCH_DIRS = ['/dev', '/dev/mapper', '/dev/md'] + glob("/dev/disk/by-*")


def resolve_device(spec, run_cmd):
    if "=" in spec:
        device = run_cmd("blkid -t %s -o device" % spec)[1].strip()
    elif not spec.startswith('/'):
        for devdir in SEARCH_DIRS:
            device = "%s/%s" % (devdir, spec)
            if os.path.exists(device):
                break
            else:
                device = ''
    else:
        device = spec

    return device


def run_module():
    module_args = dict(
        spec=dict(type='str')
    )

    result = dict(
        device=None,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result['device'] = resolve_device(module.params['spec'], run_cmd=module.run_command)
    if not os.path.exists(result['device']):
        module.fail_json(msg="The {} device spec could not be resolved".format(module.params['spec']))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
