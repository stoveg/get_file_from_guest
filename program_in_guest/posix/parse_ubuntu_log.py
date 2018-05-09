# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys
import re
import json
import threading

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag,end_file
from program_in_guest.utils import output_directory, save_directory
from program_in_guest.utils import BASE_FILE_NAME

LOG = logging.getLogger(__name__)

infile_dir='/var/log'
infile_list = ['auth.log']
base_file_path=os.path.join(os.path.dirname(__file__),BASE_FILE_NAME+'.base_auth')
end_flag_list=[]


def parse_ubuntu_log(file_name, mark):
    output_path = os.path.join(output_directory, file_name)
    input_path = os.path.join(infile_dir, file_name)
    save_path = os.path.join(save_directory, file_name + '.json')

    try:
        with open(save_path, 'w')as save_file:
            with open(input_path, 'rb')as in_file:
                for line in in_file:
                    if not line:
                        break
                    date = " ".join(line.split(' ')[0:2])
                    time = " ".join(line.split(' ')[2:3])
                    host = " ".join(line.split(' ')[3:4])
                    info = " ".join(line.split(' ')[4:]).rstrip()
                    loginfo = re.search(
                        r'((Created|Removed) slice User Slice of) (?P<user>\w+)|(Starting|Stopping|Stopped) User Manager for UID \w+.+'
                        r'|Started Session \w+ of user (\w+)', info)
                    ssh_login_success = re.search(
                        r'Accepted password for (?P<user>\w+) from (?P<ip>\d+\.\d+\.\d+\.\d+) (port)? (\d+)? (ssh)?(\d)?',
                        info)
                    ssh_login_fail = re.search(
                        r'Failed password for (invalid user)? (?P<user>\w+) from (?P<ip>\d+\.\d+\.\d+\.\d+) (port)? (\d+)? (ssh)?(\d)?',
                        info)
                    data = {'date': date, 'time': time, 'host': host, 'info': info}
                    if loginfo:
                        data['loginfo'] = loginfo.group()
                    if ssh_login_success:
                        data['ssh_login_success'] = ssh_login_success.group()
                    if ssh_login_fail:
                        data['ssh_login_fail'] = ssh_login_fail.group()
                    json.dump(data, save_file, skipkeys=True, ensure_ascii=False, separators=(',', ':'),
                              sort_keys=False)
                    save_file.write('\n')
        with open(output_file(output_path), 'w')as f:
            f.write(json.dumps({'json_file': file_name + '.json', 'save_directory': save_directory, 'error': None,
                                'mark': mark}))
        write_end_flag(output_path)
        end_flag_list.append(end_file(output_path))
    except Exception, ex:
        LOG.warn('{}'.format(str(ex)))
        with open(output_file(output_path), 'w')as f:
            f.write(json.dumps({'json_file': file_name + '.json', 'save_directory': save_directory, 'error': str(ex),
                                'mark': mark}))


def main(mark):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    LOG.info(str(os.path.split(__file__)[1]) + " is running")
    threads = []
    for file_name in infile_list:
        threads.append(threading.Thread(target=parse_ubuntu_log, args=(file_name, mark)))
    for t in threads:
        t.setDaemon(True)
        t.start()
    for t in threads:
        t.join()
    with open(base_file_path, 'w') as f:
        f.write('start\n')
        for end_flag in end_flag_list:
            f.write(end_flag + '\n')
        f.write('end')

if __name__ == '__main__':
    if len(sys.argv)>1:
        mark = sys.argv[1]
        main(mark)
    else:
        main(mark=None)
