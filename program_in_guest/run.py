# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import platform
import threading
import subprocess
import logging
import sys

sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
LOG = logging.getLogger(__name__)


def exec_cmd(cmd):
    subprocess.check_call(cmd, shell=True)


def main():
    mark = sys.argv[1]
    if os.name == "nt":
        work_directory = os.path.join(os.path.split(__file__)[0], "nt")
        os.chdir(work_directory)
        if platform.platform(0, 1).lower() == "windows-7" or platform.platform(0, 1).lower() == "windows-10":
            import program_in_guest.nt.run_parse_evtx as run_parse_evtx
            import program_in_guest.nt.parse_iis_log as parse_iis_log
            run_parse_evtx.main(mark)
            parse_iis_log.main(mark)
            # threading.Thread(target=exec_cmd, args=(cmd,)).start()
        if platform.platform(0, 1) == "Windows-XP":
            import program_in_guest.nt.parse_evt as parse_evt
            parse_evt.main(mark)
            # threading.Thread(target=exec_cmd, args=(cmd,)).start()

    if os.name == "posix":
        work_directory = os.path.join(os.path.split(__file__)[0], "posix")
        os.chdir(work_directory)
        if 'ubuntu' in platform.platform().lower():
            import program_in_guest.posix.parse_ubuntu_log as parse_ubuntu_log
            parse_ubuntu_log.main(mark)
        if 'centos' in platform.platform().lower():
            import program_in_guest.posix.parse_nginx_log as parse_nginx_log
            import program_in_guest.posix.parse_apache_log as parse_apache_log
            import program_in_guest.posix.parse_centos_log as parse_centos_log
            parse_centos_log.main(mark)
            parse_apache_log.main(mark)
            parse_nginx_log.main(mark)


if __name__ == '__main__':
    main()
