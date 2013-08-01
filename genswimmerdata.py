#!/usr/bin/env python

import pwswimmeets
import argparse
import json
import logging
log = logging.getLogger()

league_abbrev = pwswimmeets.settings.LEAGUE['abbrev']

def main():
    args = initargs()
    print args
    initlogging(args.debug)
    loadTeams(args.teams)
    seasonrange = range(2009,pwswimmeets.swimming.CURRSEASON+1)
    if args.season is not None:
        seasonrange = [args.season]
    for season in seasonrange:
        swimmers = gen_swimmers(args.dir,team_name=args.name,team_abbrev=args.abbrev,season=season,meet_date=args.date,league_abbrev=league_abbrev)

def gen_swimmers(dirname,**kwargs):
    swimmers = pwswimmeets.utils.gen_meet_results(**kwargs)
    for t in pwsimmeets.swimming.TEAMS:
        if t.league['abbrev'] != league_abbrev:
            continue
        team_abbrev = t.abbrevs[0].abbrev
        swimmerfile = dirname+'/swimmers_'+team_abbrev+".json"
        swims = [s for s in pwswimmeets.swimming.SWIMMERS if s.team is t]
        json.dump([s.json for s in swims],open(swimmerfile,'w'))

def loadTeams(teamfile):
    if teamfile is None:
        teams = pwswimmeets.utils.gen_teams()
    else:
        teams = json.load(open(teamfile,'r'))
        for js in teams:
            tid = js['ids'][0]
            t = getTeam(tid=tid['id'],source=tid['source'])
            t.load(js)

def initargs():
    teamfile = pwswimmeets.settings.DATAFILES['TEAMS']
    parser = argparse.ArgumentParser("Generate Swimmer Data")
    parser.add_argument('dir', help='Destination dir to hold json files')
    parser.add_argument('--teams',help='Location of TEAMS json file',default=teamfile)
    parser.add_argument('--debug', action='store_true',help='Enable debug output')
    filters = parser.add_argument_group('Filters','Filter collected data based on parameters.')
    filters.add_argument('--name',help='Team Name')
    filters.add_argument('--abbrev',help='Team Abbrev')
    filters.add_argument('--season',help='Season')
    filters.add_argument('--date',help='Meet Date')
    args = parser.parse_args()
    return args

def initlogging(debug):
    log.addHandler(logging.StreamHandler())
    if debug:
        log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    main()
