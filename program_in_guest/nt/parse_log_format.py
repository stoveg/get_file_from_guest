# -*-coding:utf-8-*-
import json
import re
import sys
import os
import logging

LOG=logging.getLogger(__name__)


class LogInfo(object):
    def __init__(self, regex, log_entry, outfile):
        self.log_entry = log_entry
        self.regex = regex
        log = re.match(regex, log_entry)
        json.dump(log.groupdict(), outfile, skipkeys=True, ensure_ascii=False, separators=(',', ':'), sort_keys=False)

        # print log.groupdict()
        outfile.write('\n')


class Parser(object):
    def __init__(self, format_string):
        # TODO parse format string
        self.format_list = self.get_format_list(format_string)
        self.regex = " ".join(self.get_regex_list(self.format_list))

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

    def get_regex_list(self, format_list):
        regex_list = []
        for word in format_list:
            regex_list.append(self.get_regex_dict(format_list)[word])
        return regex_list

    def parse(self, log_entry, outfile):
        # TODO parse log entry
        return LogInfo(self.regex, log_entry, outfile)

def demo():
    format_string = '''
        $remote_addr - $remote_user [$time_local] "$request" 
        $status $body_bytes_sent "$http_referer" 
        "$http_user_agent"
        '''
    log_parser = Parser(format_string)
    outfile = open('access.log.json', 'w')
    with open('access.log', 'r') as doc:
        for log_entry in doc:
            log_parser.parse(log_entry, outfile)
    outfile.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    demo()
