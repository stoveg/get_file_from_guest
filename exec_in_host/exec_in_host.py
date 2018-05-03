# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import logging
import subprocess
import sys

LOG = logging.getLogger(__name__)
sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
from program_in_guest.utils import output_file, end_file
from program_in_guest.utils import infile_directory, output_directory, save_directory

VMRUN_PATH = None

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


def put_file(vm_path, guest_path, file_path, guest, password):
    cmd1 = [VMRUN_PATH, '-T', 'ws', '-gu', guest, '-gp', password, 'copyFileFromHostToGuest']
    cmd2=['"',vm_path,'"']
    cmd3=[file_path, guest_path]
    cmd='{0} {1} {2}'.format(' '.join(cmd1),''.join(cmd2),' '.join(cmd3))
    LOG.debug('EXEC: %s', cmd)
    subprocess.check_call(cmd)


def get_file(vm_path, guest_path, file_path, guest, password):
    cmd1 = [VMRUN_PATH, '-T', 'ws', '-gu', guest, '-gp', password, 'copyFileFromGuestToHost']
    cmd2=['"',vm_path,'"']
    cmd3=[guest_path, file_path]
    cmd='{0} {1} {2}'.format(' '.join(cmd1),''.join(cmd2),' '.join(cmd3))
    LOG.debug('EXEC: %s', cmd)
    subprocess.check_call(cmd)


def exec_program(guest, password, vm_path, program, guest_python_path):
    cmd1 = [VMRUN_PATH, '-T', 'ws', '-gu', guest, '-gp', password, 'runProgramInGuest']
    cmd2 = ['"', vm_path, '"']
    # cmd = '{0} {1} {2} "{3}" "{4} "{5}"" '.format(' '.join(cmd1), ''.join(cmd2), '-interactive',
    #                                               'C:\Windows\System32\cmd.exe', '/c start', program)
    cmd = '{0} {1} {2} {3} {4} {5}'.format(' '.join(cmd1), ''.join(cmd2), '-interactive', guest_python_path,
                                           program,
                                           "haha")
    LOG.debug('EXEC: %s', cmd)
    subprocess.check_call(cmd)


def fetch(vm_path, guest_path, file_path, guest, password):
    get_file(vm_path, os.path.join(output_directory, end_file(os.path.basename(guest_path))),
             os.path.join(file_path, end_file(os.path.basename(guest_path))), guest, password)  # 1.取end文件
    with open(os.path.join(file_path, end_file(os.path.basename(guest_path))), 'r')as f:
        for line in f:
            if 'end' in line:
                get_file(vm_path, os.path.join(output_directory, output_file((os.path.basename(guest_path)))),
                         os.path.join(file_path, output_file(os.path.basename(guest_path))), guest,
                         password)  # 2.取output文件
                with open(os.path.join(file_path, output_file(os.path.basename(guest_path))), 'r')as f1:
                    for line_ in f1:
                        if 'output_file' in line_:
                            guest_file = json.loads(line_)['save_directory'] + os.path.sep + json.loads(line_)[
                                'output_file']
                            get_file(vm_path, guest_file, os.path.join(file_path, json.loads(line_)['output_file']),
                                     guest, password)


def demo_win7():
    vm_path = r"H:\shiyan\os\windows7x64\Windows 7 x64.vmx"
    guest_path = r"C:\tmp\1\System.evtx"
    file_path = r"E:\tmp\2"
    guest = 'SXY'
    password = '1234'
    program_in_guest = r'C:\tmp\get_file_from_guest\program_in_guest\run.py'
    guest_python_path = r'C:\develop\Python27\python.exe'
    exec_program(guest, password, vm_path, program_in_guest, guest_python_path)
    fetch(vm_path, guest_path, file_path, guest, password)
    # get_file(vm_path,guest_path,file_path,guest,password)


def demo_winXP():
    vm_path = r"H:\shiyan\os\XP A\Windows XP A.vmx"
    guest_path = r"C:\tmp\1\SysEvent.Evt"
    file_path = r"E:\tmp\2"
    guest = 'Administrator'
    password = '1234'
    program_in_guest = r'C:\tmp\get_file_from_guest\program_in_guest\run.py'
    guest_python_path = r'C:\Python27\python.exe'
    exec_program(guest, password, vm_path, program_in_guest, guest_python_path)
    fetch(vm_path, guest_path, file_path, guest, password)
    # get_file(vm_path, guest_path, file_path, guest, password)


def demo_ubuntu():
    vm_path = r"H:\shiyan\os\Ubuntu1604\Ubuntu.vmx"
    guest_path = r"/home/stoveg/tmp/1/auth.log"
    file_path = r"E:\tmp\2"
    guest = 'stoveg'
    password = 'os1234'
    program_in_guest = r'/home/stoveg/tmp/get_file_from_guest/program_in_guest/run.py'
    guest_python_path = '/usr/bin/python.exe'
    exec_program(guest, password, vm_path, program_in_guest, guest_python_path)
    fetch(vm_path, guest_path, file_path, guest, password)
    # get_file(vm_path, guest_path, file_path, guest, password)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # demo_winXP()
    demo_win7()
    # demo_ubuntu()
