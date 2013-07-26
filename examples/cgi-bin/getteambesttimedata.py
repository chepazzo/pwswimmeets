#!/usr/bin/env python

import pwswimmeets
#import pwswimmeets_old as pwswimmeets
import cgi
import json

form = cgi.FieldStorage()
team = form.getvalue("team", None)

pwswimmeets.settings.DATAFILES['SWIMMERS'] = 'data/vosdswimmers.json'
pwswimmeets.settings.DATAFILES['TEAMS'] = 'data/teams.json'

#teamstats = pwswimmeets.utils.get_team_best(team_abbrev=team)
#from pprint import pprint as pp
#pp(teamstats)

print "Content-type: application/json"
print
print json.dumps(pwswimmeets.utils.get_team_best(team_abbrev=team))

