# -*-coding:utf-8-*-
import threading
import Evt.Evt as evt
import sys
import subprocess
import os
from Evt.BinaryParser import read_word
import json

sys.path.append(os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0])
from program_in_guest.utils import output_file, write_end_flag
import logging
from program_in_guest.utils import infile_directory,output_directory,save_directory
LOG = logging.getLogger(__name__)

infile_list = ['SecEvent.Evt', 'SysEvent.Evt']

def parse_evt(file_name,mark):
    output_path = output_directory + os.sep + file_name
    input_path = infile_directory + os.sep + file_name
    save_path = save_directory + os.sep + file_name + '.json'

    try:
        with open(save_path, 'w')as save_file:
            with open(input_path, 'rb')as in_file:
                analyzer = evt.EvtCarver(in_file)
                for entry in analyzer.carve():
                    Block = evt.Record(entry, 0x0)
                    record_id = Block.structure_size(entry, 0x08, Block)
                    event_id = read_word(entry, 0x14)
                    date = Block.unpack_unixtime(offset=0x0c).date()
                    time = Block.unpack_unixtime(offset=0x0c).time()
                    source = Block.source()
                    event_type = read_word(entry, 0x18)
                    category = read_word(entry, 0x1c)
                    part, _, rest = Block.unpack_string(0x38 + len(source) * 2 + 0x02,
                                                        len(entry) - (0x40 + len(source) * 2)).partition('\x00\x00')
                    if len(part) % 2 == 1 or (len(rest) > 0 and rest[0] == "\x00"):
                        part += "\x00"
                    computer = part.decode("utf-16le")
                    part, _, rest = Block.unpack_binary(Block.structure_size(entry, 0x24, Block),
                                                        len(entry) - Block.structure_size(entry, 0x24,
                                                                                          Block)).partition('\x00\x00')
                    # if len(part) %2 == 1 or (len(rest) > 0 and rest[0] == "\x00"):
                    #   part +="\x00"
                    data = {"record_id": record_id, "event_type": event_type, "date": str(date), "time": str(time),
                            "source": str(source), "category": category, "event_id": event_id,
                            "computer": str(computer)}
                    json.dump(data, save_file, skipkeys=True, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
                    save_file.write('\n')

        with open(output_file(output_path), 'w')as f:
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
    LOG.info(str(os.path.split(__file__)[1]) + " is running")
    for infile in infile_list:
        threading.Thread(target=parse_evt, args=(infile,mark)).start()


if __name__ == '__main__':
    main(mark=None)
