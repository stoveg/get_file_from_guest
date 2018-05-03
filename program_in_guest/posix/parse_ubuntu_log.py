# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import sys
import re
import json
import threading

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag
from program_in_guest.utils import infile_directory, output_directory, save_directory

LOG = logging.getLogger(__name__)

infile_list = ['syslog', 'auth.log']


# infile_directory = r'E:\tmp\1'
# output_directory = r'E:\tmp\output'
# save_directory = r'E:\tmp\save'
# infile_directory = r'/home/stoveg/tmp/1'
# output_directory = r'/home/stoveg/tmp/output'
# save_directory = r'/home/stoveg/tmp/save'



def parse_ubuntu_log(file_name, mark):
    output_path = output_directory + os.sep + file_name
    input_path = infile_directory + os.sep + file_name
    save_path = save_directory + os.sep + file_name + '.json'

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
                    login_success = re.search(
                        r'Accepted password for (?P<user>\w+) from (?P<ip>\d+\.\d+\.\d+\.\d+) (port)? (\d+)? (ssh)?(\d)?',
                        info)
                    login_fail = re.search(
                        r'Failed password for (invalid user)? (?P<user>\w+) from (?P<ip>\d+\.\d+\.\d+\.\d+) (port)? (\d+)? (ssh)?(\d)?',
                        info)
                    data = {'date': date, 'time': time, 'host': host, 'info': info}
                    if loginfo:
                        data['loginfo'] = loginfo.group()
                    if login_success:
                        data['login_success'] = login_success.group()
                    if login_fail:
                        data['login_fail'] = login_fail.group()
                    json.dump(data, save_file, skipkeys=True, ensure_ascii=False, separators=(',', ':'),
                              sort_keys=False)
                    save_file.write('\n')
        with open(output_file(output_path), 'w')as f:
            f.write(json.dumps({'output_file': file_name + '.json', 'save_directory': save_directory, 'error': None,
                                'mark': mark}))
        write_end_flag(output_path)
    except Exception, ex:
        LOG.warn('{}'.format(str(ex)))
        with open(output_file(output_path), 'w')as f:
            f.write(json.dumps({'output_file': file_name + '.json', 'save_directory': save_directory, 'error': str(ex),
                                'mark': mark}))


def main(mark):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    LOG.info(str(os.path.split(__file__)[1]) + " is running")
    for file_name in infile_list:
        threading.Thread(target=parse_ubuntu_log, args=(file_name, mark)).start()


if __name__ == '__main__':
    main(mark=None)
