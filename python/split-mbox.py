import os
from os.path import isfile, join
import argparse

def split_mbox(input, output="out"):
    if output is None:
        output = "out"
    try:
        os.mkdir(output)
    except:
        pass
    if input:
        files = [f for f in os.listdir(input) if isfile(join(input, f)) and f.endswith(".mbox")]
        for file in files:
            print "Splitting {0}".format(file)
            out_file = None
            with open(join(input, file)) as f:
                sub_dir = join(output, file)
                try:
                    os.mkdir(sub_dir)
                except:
                    pass
                i = 0
                for line in f:
                    if line.find("From") == 0:
                        print "Opening new file for {0}".format(line)
                        if out_file:
                            out_file.close()
                        out_file = open(join(sub_dir, "mail_{0}.mbox".format(i)), 'w')
                        i += 1
                    out_file.write(line)
            if out_file:
                try:
                    out_file.close()
                except:
                    pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Setup Search Hub')
    parser.add_argument('--input', action='store', help='The mbox files to split')
    parser.add_argument('--output', action='store', help='The mbox files to split')
    cmd_args = parser.parse_args()
    split_mbox(cmd_args.input, cmd_args.output)
