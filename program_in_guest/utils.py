# -*-coding:utf-8-*-
import logging

LOG = logging.getLogger(__name__)
import os

BASE_FILE_NAME='base.txt'

if os.name == "nt":
    infile_directory=r'C:\tmp\1'
    output_directory = r'C:\tmp\output'
    save_directory = r'C:\tmp\save'
if os.name == "posix":
    infile_directory = '/home/stoveg/tmp/1'
    output_directory = r'/home/stoveg/tmp/output'
    save_directory = r'/home/stoveg/tmp/save'


def output_file(file_path):
    return file_path + '.output'


def end_file(file_path):
    return file_path + '.end'


def write_end_flag(file_path):
    try:
        with open(end_file(file_path), 'w') as f:
            f.write('end')
    except Exception, ex:
        LOG.warn("write_end_flag failed: {0}".format(ex))
