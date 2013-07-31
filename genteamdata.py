#!/usr/bin/env python

import pwswimmeets
import argparse
import json
import logging
log = logging.getLogger()

def main():
    args = initargs()
    initlogging(args.debug)
    gen_teams(args.file)

def gen_teams(filename):
    pwswimmeets.utils.gen_teams()
    json.dump([t.json for t in pwswimmeets.swimming.TEAMS],open(filename,'w'))

def initargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='json file destination',default=pwswimmeets.settings.DATAFILES['TEAMS'])
    parser.add_argument('--debug', action='store_true',help='Enable debug output')
    args = parser.parse_args()
    if args.file is None:
        print "You need to specify a filename either on the cmdline or in your settings file."
        parser.print_help()
        exit()
    return args

def initlogging(debug):
    log.addHandler(logging.StreamHandler())
    if debug:
        log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    main()
