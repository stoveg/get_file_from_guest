#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import re
import json
import logging
import threading

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag
from program_in_guest.utils import infile_directory,output_directory,save_directory

'''
access_log for apache
'''

LOG = logging.getLogger(__name__)

infile_list = ['access_log']
# infile_directory = r'/home/stoveg/tmp/1'
# output_directory = r'/home/stoveg/tmp/output'
# save_directory = r'/home/stoveg/tmp/save'


def parse_apache_log(file_name,mark):
    output_path = output_directory + os.sep + file_name
    input_path = infile_directory + os.sep + file_name
    save_path = save_directory + os.sep + file_name + '.json'

    try:
        with open(save_path, 'w')as save_file:
            with open(input_path, 'rb')as in_file:
                for line in in_file:
                    if not line:
                        break
                    m = re.search(
                        r'(?P<remote_addr>.*) - (?P<remote_user>.*) \[(?P<time_local>.*)\] \"(?P<request>.*)\" (?P<status>.*) (?P<bytes_sent>.*) \"(?P<URL>.*)\" \"(?P<user_agent>.*)\"',
                        line)

                    data = {}
                    data['remote_addr'] = m.group(1)
                    data['remote_user'] = m.group(2)
                    data['time_local'] = m.group(3)
                    data['request'] = m.group(4)
                    data['status'] = m.group(5)  # 2xx-success  3xx-redirection 4xx-error_in_client 5xx-error_in_server
                    data['bytes_sent'] = m.group(6)
                    data['URL'] = m.group(7)
                    data['user_agent'] = m.group(8)
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
    LOG.info(str(os.path.split(__file__)[1]) + " is running")
    for file_name in infile_list:
        threading.Thread(target=parse_apache_log, args=(file_name,mark)).start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    main(mark=None)
