# encoding=utf-8
import logging
import optparse
import Evtx.Evtx as evtx
import sys
import codecs
import json
import os
import xmltodict
sys.path.append((os.path.split(__file__)[0]))
print sys.path
sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import save_directory

LOG = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf-8')


def get_options():
    option_list = [
        optparse.make_option("-f", "--file", dest="file", help="the path to log file"),
        optparse.make_option("-p", "--pattern", dest="pattern", help="the search pattern")
    ]
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage, option_list=option_list)
    opts, args = parser.parse_args()
    if not opts.file or not opts.pattern:
        raise ValueError("Path is required")
    return opts


def parse_evtx(opts):
    with open(save_directory + os.sep + os.path.split(opts.file)[1] + '.json', 'w')as outfile:
        #outfile.write(codecs.BOM_UTF8)
        with evtx.Evtx(opts.file.strip()) as log:
            for chunk in log.chunks():
                for record in chunk.records():
                    xml = record.xml()
                    xmlstr = xmltodict.parse(xml, encoding='utf-8')
                    json.dump(xmlstr, outfile, skipkeys=True, ensure_ascii=False, separators=(',', ':'), encoding='utf-8',
                              sort_keys=True)
                    outfile.write('\n')


def main():
    opts = get_options()
    LOG.debug("Start analyzing EVTX")
    parse_evtx(opts)
    LOG.debug("EVTX analysis ends")


if __name__ == '__main__':
    main()
