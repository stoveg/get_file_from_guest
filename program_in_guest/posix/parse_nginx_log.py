# !/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import sys
import os
import logging
import threading
import abc

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag, end_file, BASE_FILE_NAME
from program_in_guest.utils import output_directory,save_directory

LOG = logging.getLogger(__name__)

infile_dir='/usr/local/nginx/logs'
infile_list = ['access.log']
base_file_path=os.path.join(os.path.dirname(__file__),BASE_FILE_NAME+'.base_nginx')
end_flag_list=[]

class LogInfo(object):
    def __init__(self, regex, log_entry, outfile):
        self.log_entry = log_entry
        self.regex = regex
        log = re.match(regex, log_entry)
        json.dump(log.groupdict(), outfile, skipkeys=True, ensure_ascii=False, separators=(',', ':'), sort_keys=False)
        outfile.write('\n')


class Parser(object):
    def __init__(self, regex, format_list):
        self.regex = regex
        self.format_list = format_list

    def get_format_list(self, format_string):
        format_list = []
        for x in format_string.split():
            if x.startswith('$'):
                format_list.append(x[1:])
            elif x.startswith('[') or x.startswith('"'):
                format_list.append(x.strip('[]"')[1:])
            else:
                format_list.append(x)
        return format_list

    def get_regex_list(self, format_list):
        regex_list = []
        for word in format_list:
            regex_list.append(self.get_regex_dict(format_list)[word])
        return regex_list

    def parse(self, log_entry, outfile):
        # TODO parse log entry
        return LogInfo(self.regex, log_entry, outfile)

    @abc.abstractmethod
    def get_regex_dict(self, format_list):
        pass


class NginxParser(Parser):
    def __init__(self, format_string):
        # TODO parse format string
        format_list = self.get_format_list(format_string)
        regex = " ".join(self.get_regex_list(format_list))
        super(NginxParser, self).__init__(regex, format_list)

    def get_regex_dict(self, format_list):
        regex_dict = {}
        for i, key in enumerate(format_list):
            if key == 'remote_addr':
                regex_dict[key] = r'(?P<remote_addr>([\d]{1,3}\.){3}[\d]{1,3})'
            if key == '-':
                regex_dict[key] = r'(-)'
            if key == 'remote_user':
                regex_dict[key] = r'(?P<remote_user>\S+)'
            if key == 'time_local':
                regex_dict[key] = r'\[(?P<time_local>[^\[\]]+)\]'
            if key == 'request':
                regex_dict[key] = r'"(?P<request>(GET|P(OS|U)T|HEAD|OPTIONS|DELETE|TRAC(E|K)|CONNECT|ACUNETIX)[^"]+)"'
            if key == 'status':
                regex_dict[key] = r'(?P<status>\d+)'
            if key == 'body_bytes_sent':
                regex_dict[key] = r'(?P<body_bytes_sent>\d+)'
            if key == 'http_referer':
                regex_dict[key] = r'"(?P<http_referer>[^"]+)"'
            if key == 'http_user_agent':
                regex_dict[key] = r'"(?P<http_user_agent>[^"]+)"'
            if key == 'http_x_forwarded_for':
                regex_dict[key] = r'(?P<http_x_forwarded_for>([\d]{1,3}\.){3}[\d]{1,3})'
            if key == 'http_host':
                regex_dict[key] = r'(?P<http_host>[\w\.]{7,}+)'
            if key == 'upstream_status':
                regex_dict[key] = r'(?P<upstream_status>\d+)'
            if key == 'ssl_protocol':
                regex_dict[key] = r'(?P<ssl_protocol>\w+)'
            if key == 'ssl_cipher':
                regex_dict[key] = r'(?P<ssl_cipher>[-\w]+)'
            if key == 'upstream_addr':
                regex_dict[key] = r'(?P<upstream_addr>([\d]{1,3}\.){3}[\d]{1,3}:?[\d]+?)'
            if key == 'request_time':
                regex_dict[key] = r'(?P<request_time>[\d\.]{,10})'
            if key == 'upstream_response_time':
                regex_dict[key] = r'(?P<upstream_response_time>[\d\.]{,10})'
        return regex_dict


def parse_nginx_log(file_name, format_string, mark):
    output_path = os.path.join(output_directory, file_name)
    input_path = os.path.join(infile_dir, file_name)
    save_path = os.path.join(save_directory, file_name + '.json')

    log_parser = NginxParser(format_string)
    try:
        with open(save_path, 'w')as save_file:
            with open(input_path, 'rb')as in_file:
                for log_entry in in_file:
                    log_parser.parse(log_entry, save_file)
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
    format_string = '''
        $remote_addr - $remote_user [$time_local] "$request" 
        $status $body_bytes_sent "$http_referer" 
        "$http_user_agent"
        '''
    LOG.info(str(os.path.split(__file__)[1]) + " is running")
    threads = []
    for file_name in infile_list:
        threads.append(threading.Thread(target=parse_nginx_log, args=(file_name,format_string, mark)))
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