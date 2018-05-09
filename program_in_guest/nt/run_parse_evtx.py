# -*-coding:utf-8-*-
import json
import logging
import os
import subprocess
import sys
import threading

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag, end_file
from program_in_guest.utils import output_directory, save_directory
from program_in_guest.utils import BASE_FILE_NAME

LOG = logging.getLogger(__name__)

infile_dir = r'C:\Windows\System32\winevt\Logs'
infile_list = [r'System.evtx', r'Security.evtx', r'Setup.evtx']
base_file_path = os.path.join(os.path.dirname(__file__), BASE_FILE_NAME + '.base_evtx')
end_flag_list = []


def exec_cmd(cmd, file_name, mark):
    output_path = os.path.join(output_directory, file_name)
    try:
        subprocess.check_call(cmd, shell=True)
        with open(output_file(output_path), 'w') as f:
            f.write(
                json.dumps({'json_file': file_name + '.json', 'save_directory': save_directory, 'error': None,
                            'mark': mark}))
        write_end_flag(output_path)
        end_flag_list.append(end_file(output_path))

    except Exception, ex:
        LOG.warn('{}'.format(str(ex)))
        with open(output_file(output_path), 'w') as f:
            f.write(
                json.dumps({'json_file': file_name + '.json', 'save_directory': save_directory, 'error': str(ex),
                            'mark': mark}))


def main(mark):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    LOG.info(str(os.path.split(__file__)[1]) + " is running")
    threads = []
    for file_name in infile_list:
        cmd1 = '{0} {1} {2} {3} {4}'.format("python", os.path.join(os.path.dirname(__file__), 'parse_evtx.py'), "-f",
                                            infile_dir + os.sep + str(file_name), "-p Event")
        threads.append(threading.Thread(target=exec_cmd, args=(cmd1, file_name, mark)))
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
    if len(sys.argv) > 1:
        mark = sys.argv[1]
        main(mark)
    else:
        main(mark=None)
