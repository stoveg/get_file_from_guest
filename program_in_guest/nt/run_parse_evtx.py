# -*-coding:utf-8-*-
import json
import logging
import os
import subprocess
import sys
import threading

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag
from program_in_guest.utils import infile_directory,output_directory,save_directory

LOG = logging.getLogger(__name__)

infile_list = [r'System.evtx', r'Security.evtx', r'Setup.evtx']

def exec_cmd(cmd, file_name,mark):
    output_path = output_directory + os.sep + file_name
    try:
        subprocess.check_call(cmd, shell=True)
        with open(output_file(output_path), 'w') as f:
            f.write(
                json.dumps({'output_file': file_name + '.json', 'save_directory': save_directory, 'error': None,
                            'mark': mark}))
        write_end_flag(output_path)

    except Exception, ex:
        LOG.warn('{}'.format(str(ex)))
        with open(output_file(output_path), 'w') as f:
            f.write(
                json.dumps({'output_file': file_name + '.json', 'save_directory': save_directory, 'error': str(ex),
                            'mark': mark}))


def main(mark):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    LOG.info(str(os.path.split(__file__)[1])+" is running")
    for file_name in infile_list:
        cmd1 = '{0} {1} {2}' .format("python parse_evtx.py -f", infile_directory + os.sep + str(file_name), "-p Event")
        threading.Thread(target=exec_cmd, args=(cmd1, file_name,mark)).start()

if __name__ == '__main__':
    main(mark=None)
