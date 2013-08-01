#!/usr/bin/env python

import pwswimmeets
import cgi
import json

form = cgi.FieldStorage()
team = form.getvalue("team", None)
season = form.getvalue("season", None)

pwswimmeets.settings.DATAFILES['SWIMMERS'] = '/opt/web/sites/MISHAP/data/swimmers/swimmers_VOS.json'
pwswimmeets.settings.DATAFILES['TEAMS'] = '/opt/web/sites/MISHAP/data/pwslteams.json'

if season is not None:
    pwswimmeets.swimming.CURRSEASON = int(season)

print "Content-type: application/json"
print
print json.dumps(pwswimmeets.utils.get_team_best(team_abbrev=team))

