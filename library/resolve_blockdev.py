#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: resolve_device
short_description: Resolve block device specification to device node path.
version_added: "2.5"
description:
    - "This module accepts various forms of block device identifiers and
       resolves them to the correct block device node path."
options:
    spec:
        description:
            - String describing a block device
        required: true
author:
    - David Lehman (dlehman@redhat.com)
'''

EXAMPLES = '''
- name: Resolve device by label
  resolve_device:
    spec: LABEL=MyData

- name: Resolve device by name
  resolve_device:
    spec: mpathb

- name: Resolve device by /dev/disk/by-id symlink name
  resolve_device:
    spec: wwn-0x5000c5005bc37f3f
'''

RETURN = '''
device:
    description: Path to block device node
    type: str
'''

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
