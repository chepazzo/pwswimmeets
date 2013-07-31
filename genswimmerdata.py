#!/usr/bin/env python

import pwswimmeets
import argparse
import json
import logging
log = logging.getLogger()

def main():
    args = initargs()
    print args
    #initlogging(args.debug)
    #gen_swimmers(args.dir)

def gen_swimmers(dirname,**kwargs):
    pwswimmeets.utils.gen_meet_results(**kwargs)
    json.dump([t.json for t in pwswimmeets.swimming.TEAMS],open(filename,'w'))

def initargs():
    parser = argparse.ArgumentParser("Generate Swimmer Data")
    parser.add_argument('dir', help='Destination dir to hold json files')
    parser.add_argument('--teams',help='Location of TEAMS json',default=pwswimmeets.settings.DATAFILES['TEAMS'])
    parser.add_argument('--debug', action='store_true',help='Enable debug output')
    filters = parser.add_argument_group('Filters','Filter collected data based on parameters.')
    filters.add_argument('--name',help='Team Name')
    filters.add_argument('--abbrev',help='Team Abbrev')
    filters.add_argument('--season',help='Season')
    filters.add_argument('--date',help='Meet Date')
    args = parser.parse_args()
    if args.teams is None:
        print "You need to specify a list of teams because there are too many to grab all data for all of them."
        parser.print_help()
        exit()
    return args

def initlogging(debug):
    log.addHandler(logging.StreamHandler())
    if debug:
        log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    main()
