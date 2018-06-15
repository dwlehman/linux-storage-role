
import os
import pytest

from resolve_device import resolve_device


blkid_data = [('LABEL=target', '/dev/sdx3'),
              ('UUID=6c75fa75-e5ab-4a12-a567-c8aa0b4b60a5', '/dev/sdaz'),
              ('LABEL=missing', '')]

path_data = ['/dev/md/unreal',
             '/dev/mapper/fakevg-fakelv',
             '/dev/adisk',
             '/dev/disk/by-id/wwn-0x123456789abc']


@pytest.mark.parametrize('spec,device', blkid_data)
def test_key_value_pair(spec, device):
    def run_cmd(args):
        for _spec, _dev in blkid_data:
            if _spec in args:
                break
        else:
            _dev = ''
        return (0, _dev, '')

    assert resolve_device(spec, run_cmd) == device


@pytest.mark.parametrize('name', [os.path.basename(p) for p in path_data])
def test_device_names(name, monkeypatch):
    def path_exists(path):
        return next((data for data in path_data if data == path), False)

    expected = next((data for data in path_data if os.path.basename(data) == name), '')
    monkeypatch.setattr(os.path, 'exists', path_exists)
    assert resolve_device(name, None) == expected


def test_device_name(monkeypatch):
    assert os.path.exists('/dev/xxx') is False

    monkeypatch.setattr(os.path, 'exists', lambda p: True)
    assert resolve_device('xxx', None) == '/dev/xxx'

    monkeypatch.setattr(os.path, 'exists', lambda p: False)
    assert resolve_device('xxx', None) == ''


def test_full_path():
    path = "/dev/idonotexist"
    assert resolve_device(path, None) == path

    path = "/dev/disk/by-label/alabel"
    assert resolve_device(path, None) == path
