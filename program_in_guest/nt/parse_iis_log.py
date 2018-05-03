# -*-coding:utf-8-*-
import json
import threading
import sys
import logging
import os

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.posix.parse_nginx_log import Parser
from program_in_guest.utils import output_file, write_end_flag
from program_in_guest.utils import infile_directory, output_directory, save_directory

LOG = logging.getLogger(__name__)

infile_list = ['u_ex160408.log', 'u_ex18041907.log', 'u_ex18041908.log', ]


class LogParser(Parser):
    def __init__(self, format_string):
        # TODO parse format string
        self.format_list = format_string
        self.regex = " ".join(self.get_regex_list(self.format_list))

    def get_regex_dict(self, format_list):
        regex_dict = {}
        for i, key in enumerate(format_list):
            if key == 'date':
                regex_dict[key] = r'(?P<date>\d{4}-\d{2}-\d{2})'
            if key == 'time':
                regex_dict[key] = r'(?P<time>\d{2}:\d{2}:\d{2})'
            if key == 's-ip':
                regex_dict[key] = r'(?P<s_ip>(([\d]{1,3}\.){3}[\d]{1,3})|::1)'
            if key == 'cs-method':
                regex_dict[key] = r'(?P<cs_method>GET|P(OS|U)T|HEAD|OPTIONS|DELETE|TRAC(E|K)|CONNECT|ACUNETIX|PROPFIND)'
            if key == 'cs-uri-stem':
                regex_dict[key] = r'(?P<cs_uri_stem>\S+)'
            if key == 'cs-uri-query':
                regex_dict[key] = r'(?P<cs_uri_query>\S+)'
            if key == 's-port':
                regex_dict[key] = r'(?P<s_port>\d{1,5})'
            if key == 'cs-username':
                regex_dict[key] = r'(?P<cs_username>\S+)'
            if key == 'c-ip':
                regex_dict[key] = r'(?P<c_ip>(([\d]{1,3}\.){3}[\d]{1,3})|::1)'
            if key == 'cs(User-Agent)':
                regex_dict[key] = r'(?P<cs_User_Agent>\S+)'
            if key == 'sc-status':
                regex_dict[key] = r'(?P<sc_status>\d{3})'
            if key == 'sc-substatus':
                regex_dict[key] = r'(?P<sc_substatus>\d+)'
            if key == 'sc-win32-status':
                regex_dict[key] = r'(?P<sc_win32_status>\d+)'
            if key == 'time-taken':
                regex_dict[key] = r'(?P<time_taken>\d+)'
        return regex_dict


def get_format_string(file_path):
    format_string = None
    with open(file_path)as f:
        for line in f:
            if line.startswith('#Fields:'):
                format_string = line[8:].split()
                break
            else:
                continue
    return format_string


def parse_iis_log(file_name, mark):
    output_path = output_directory + os.sep + file_name
    input_path = infile_directory + os.sep + file_name
    save_path = save_directory + os.sep + file_name + '.json'

    format_string = get_format_string(input_path)
    log_parser = LogParser(format_string)
    try:
        with open(save_path, 'w')as save_file:
            with open(input_path, 'r')as in_file:
                for log_entry in in_file:
                    if log_entry.startswith('#'):
                        continue
                    log_parser.parse(log_entry, save_file)
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
        threading.Thread(target=parse_iis_log, args=(file_name, mark)).start()


if __name__ == '__main__':
    main(mark=None)
