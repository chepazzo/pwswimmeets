#!/usr/bin/env python

import pwswimmeets
#import pwswimmeets_old as pwswimmeets
import cgi
import json

form = cgi.FieldStorage()
name = form.getvalue("name", None)

pwswimmeets.settings.DATAFILES['TEAMS'] = '/opt/web/sites/MISHAP/data/pwslteams.json'
pwswimmeets.settings.DATAFILES['SWIMMERS'] = '/opt/web/sites/MISHAP/data/swimmers/swimmers_VOS.json'

print "Content-type: application/json"
print
print json.dumps(pwswimmeets.utils.get_best_times(name))
#print json.dumps(pwswimmeets.utils.get_best_times(name,source='rftw'))

