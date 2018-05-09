# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import logging
import subprocess
import sys

import time

LOG = logging.getLogger(__name__)
sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
from program_in_guest.utils import output_file

VMRUN_PATH = None
BASE_FILE_NAME = 'base.txt'

if os.name == 'nt':
    for drive in 'CDEFGH':
        guess_path_list = (r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
                           r"C:\Program Files\VMware\VMware Workstation\vmrun.exe",
                           r"H:\shiyan\VmWare\vmrun.exe")
        for _guess_path in guess_path_list:
            if os.path.exists(_guess_path):
                VMRUN_PATH = _guess_path
                break
        if VMRUN_PATH:
            break

    if not VMRUN_PATH:
        raise Exception("vmrun.exe not found!")
else:
    VMRUN_PATH = 'vmrun'


def put_file(vm_path, guest_path, local_file_dir, guest, password):
    cmd1 = [VMRUN_PATH, '-T', 'ws', '-gu', guest, '-gp', password, 'copyFileFromHostToGuest']
    cmd2 = ['"', vm_path, '"']
    cmd3 = [os.path.join(local_file_dir, os.path.basename(guest_path)), guest_path]
    cmd = '{0} {1} {2}'.format(' '.join(cmd1), ''.join(cmd2), ' '.join(cmd3))
    LOG.debug('EXEC COMMAND: %s', cmd)
    subprocess.check_call(cmd)


def get_file(vm_path, guest_path, local_file_dir, guest, password):
    cmd1 = [VMRUN_PATH, '-T', 'ws', '-gu', guest, '-gp', password, 'copyFileFromGuestToHost']
    cmd2 = ['"', vm_path, '"']
    cmd3 = [guest_path, os.path.join(local_file_dir, os.path.basename(guest_path))]
    cmd = '{0} {1} {2}'.format(' '.join(cmd1), ''.join(cmd2), ' '.join(cmd3))
    LOG.debug('EXEC COMMAND: %s', cmd)
    subprocess.check_call(cmd)


def exec_program(guest, password, vm_path, program, guest_python_path, mark):
    cmd1 = [VMRUN_PATH, '-T', 'ws', '-gu', guest, '-gp', password, 'runProgramInGuest']
    cmd2 = ['"', vm_path, '"']
    # cmd = '{0} {1} {2} "{3}" "{4} "{5}"" '.format(' '.join(cmd1), ''.join(cmd2), '-interactive','C:\Windows\System32\cmd.exe', '/c start', program)
    cmd = '{0} {1} {2} {3} {4} {5}'.format(' '.join(cmd1), ''.join(cmd2), '-interactive', guest_python_path, program,
                                           mark)
    LOG.debug('EXEC COMMAND: %s', cmd)
    subprocess.check_call(cmd)


def fetch(vm_path, guest_path, local_file_dir, guest, password, PATH_SEP):
    if guest_path.strip('\r\n').endswith('.end'):
        guest_path = guest_path.strip('\r\n')
        local_end_file_path = os.path.join(local_file_dir, os.path.basename(guest_path))
        get_file(vm_path, guest_path, local_file_dir, guest, password)  # 取end文件
        LOG.debug('GET: .end success')
        with open(local_end_file_path, 'r')as f:
            for line in f:
                if 'end' in line:
                    output_file_basename = output_file(os.path.basename(guest_path)[:-4])
                    local_output_file_path = os.path.join(local_file_dir, output_file_basename)
                    guest_output_file_path = os.path.dirname(guest_path) + PATH_SEP + output_file_basename
                    get_file(vm_path, guest_output_file_path, local_file_dir, guest, password)  # 取output文件
                    LOG.debug('GET: .output success')
                    with open(local_output_file_path, 'r')as f1:
                        for line_ in f1:
                            if 'error' in line_ and not json.loads(line_)['error']:
                                guest_json_file_path = json.loads(line_)['save_directory'] + PATH_SEP + \
                                                       json.loads(line_)[
                                                           'json_file']
                                get_file(vm_path, guest_json_file_path, local_file_dir, guest, password)  # 取json文件
                                LOG.debug('GET: .json success')


def fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path,
                  PATH_SEP, mark):
    exec_program(guest, password, vm_path, program_in_guest, guest_python_path, mark)  # exec
    guest_path = ''
    guest_path_list = []
    while True:
        try:
            get_file(vm_path, base_file_path, local_file_dir, guest, password)
            LOG.debug('GET:  .base success')
            local_base_file_path = os.path.join(local_file_dir, os.path.basename(base_file_path))
            with open(local_base_file_path, 'r') as f:
                flag = 0
                for line in f:
                    if line.startswith('start'):
                        continue
                    elif line.startswith('end'):
                        flag = 1
                        break
                    else:
                        guest_path = line
                        if guest_path not in guest_path_list:  # 去重
                            fetch(vm_path, guest_path, local_file_dir, guest, password, PATH_SEP)
                            guest_path_list.append(guest_path)
        except Exception, ex:
            LOG.warn('{}'.format(str(ex)))
            break
        else:
            time.sleep(5)
            if flag:
                break


def demo_evtx(mark):
    vm_path = r"H:\shiyan\os\windows7x64\Windows 7 x64.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'SXY'
    password = '1234'
    program_in_guest = r'C:\tmp\get_file_from_guest\program_in_guest\nt\run_parse_evtx.py'
    guest_python_path = r'C:\develop\Python27\python.exe'
    base_file_path = os.path.join(os.path.dirname(program_in_guest), BASE_FILE_NAME + '.base_evtx')
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '\\',
                  mark)


def demo_evt(mark):
    vm_path = r"H:\shiyan\os\XP A\Windows XP A.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'Administrator'
    password = '1234'
    program_in_guest = r'C:\tmp\get_file_from_guest\program_in_guest\nt\parse_evt.py'
    guest_python_path = r'C:\Python27\python.exe'
    base_file_path = os.path.join(os.path.dirname(program_in_guest), BASE_FILE_NAME + '.base_evt')
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '\\',
                  mark)


def demo_ubuntu(mark):
    vm_path = r"H:\shiyan\os\Ubuntu1604\Ubuntu.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'stoveg'
    password = 'os1234'
    program_in_guest = r'/home/stoveg/tmp/get_file_from_guest/program_in_guest/posix/parse_ubuntu_log.py'
    guest_python_path = '/usr/bin/python'
    base_file_path = os.path.dirname(program_in_guest) + '/' + BASE_FILE_NAME + '.base_auth'
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '/',
                  mark)


def demo_iis(mark):
    vm_path = r"H:\shiyan\os\windows7x64\Windows 7 x64.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'SXY'
    password = '1234'
    program_in_guest = r'C:\tmp\get_file_from_guest\program_in_guest\nt\parse_iis_log.py'
    guest_python_path = r'C:\develop\Python27\python.exe'
    base_file_path = os.path.join(os.path.dirname(program_in_guest), BASE_FILE_NAME + '.base_iis')
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '\\',
                  mark)


def demo_centos(mark):
    vm_path = r"H:\shiyan\os\CentOS1708\CentOS.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'stoveg'
    password = '1234os'
    program_in_guest = r'/home/stoveg/tmp/get_file_from_guest/program_in_guest/posix/parse_centos_log.py'
    guest_python_path = '/usr/bin/python'
    base_file_path = os.path.dirname(program_in_guest) + '/' + BASE_FILE_NAME + '.base_secure'
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '/',
                  mark)


def demo_apache(mark):
    vm_path = r"H:\shiyan\os\CentOS1708\CentOS.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'stoveg'
    password = '1234os'
    program_in_guest = r'/home/stoveg/tmp/get_file_from_guest/program_in_guest/posix/parse_apache_log.py'
    guest_python_path = '/usr/bin/python'
    base_file_path = os.path.dirname(program_in_guest) + '/' + BASE_FILE_NAME + '.base_apache'
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '/',
                  mark)


def demo_nginx(mark):
    vm_path = r"H:\shiyan\os\CentOS1708\CentOS.vmx"
    local_file_dir = r"E:\tmp\2"
    guest = 'stoveg'
    password = '1234os'
    program_in_guest = r'/home/stoveg/tmp/get_file_from_guest/program_in_guest/posix/parse_nginx_log.py'
    guest_python_path = '/usr/bin/python'
    base_file_path = os.path.dirname(program_in_guest) + '/' + BASE_FILE_NAME + '.base_nginx'
    fetch_by_rule(vm_path, local_file_dir, guest, password, program_in_guest, guest_python_path, base_file_path, '/',
                  mark)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    if len(sys.argv) > 1:
        mark = sys.argv[1]
    else:
        mark = None
    demo_centos(mark)
    # demo_apache(mark)
    # demo_nginx(mark)
    # demo_ubuntu(mark)

    # demo_iis(mark)
    # demo_evtx(mark)
    # demo_evt(mark)
