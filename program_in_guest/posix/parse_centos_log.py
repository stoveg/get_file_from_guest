# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import json
import re
import sys
import threading

LOG = logging.getLogger(__name__)

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag
from program_in_guest.utils import infile_directory, output_directory, save_directory

infile_list = ['messages']


# infile_directory = r'E:\tmp\1'
# output_directory = r'E:\tmp\output'
# save_directory = r'E:\tmp\save'


# infile_directory = r'/home/stoveg/tmp/1'
# output_directory = r'/home/stoveg/tmp/output'
# save_directory = r'/home/stoveg/tmp/save'


def parse_centos_log(file_name, mark):
    output_path = output_directory + os.sep + file_name
    input_path = infile_directory + os.sep + file_name
    save_path = save_directory + os.sep + file_name + '.json'
    try:
        with open(save_path, 'w')as save_file:
            with open(input_path, 'rb')as in_file:
                for line in in_file:
                    date = " ".join(line.split(' ')[0:2])
                    time = " ".join(line.split(' ')[2:3])
                    host = " ".join(line.split(' ')[3:4])
                    info = " ".join(line.split(' ')[4:]).rstrip()
                    loginfo = re.search(
                        r'((Created|Removed) slice User Slice of) (?P<user>\w+)|(Starting|Stopping|Stopped) User Manager for UID \w+.+'
                        r'|Started Session \w+ of user (\w+)', info)
                    data = {'date': date, 'time': time, 'host': host, 'info': info}
                    if loginfo:
                        data['loginfo'] = loginfo.group()
                    json.dump(data, save_file, skipkeys=True, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
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
        threading.Thread(target=parse_centos_log, args=(file_name, mark)).start()


if __name__ == '__main__':
    main(mark=None)
