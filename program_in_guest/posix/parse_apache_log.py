#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import re
import json
import logging
import threading

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag,end_file
from program_in_guest.utils import output_directory,save_directory
from program_in_guest.utils import BASE_FILE_NAME

'''
access_log for apache
'''

LOG = logging.getLogger(__name__)

infile_dir='/var/log/httpd'
infile_list = ['access_log']
end_flag_list=[]
base_file_path=os.path.join(os.path.dirname(__file__),BASE_FILE_NAME+'.base_apache')


def parse_apache_log(file_name,mark):
    output_path = os.path.join(output_directory, file_name)
    input_path = os.path.join(infile_dir, file_name)
    save_path = os.path.join(save_directory, file_name + '.json')

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
        threads.append(threading.Thread(target=parse_apache_log, args=(file_name, mark)))
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