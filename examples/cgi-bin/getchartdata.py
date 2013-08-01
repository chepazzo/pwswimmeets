#!/usr/bin/env python

import pwswimmeets
import cgi
import json

form = cgi.FieldStorage()
name = form.getvalue("name", None)

pwswimmeets.settings.DATAFILES['SWIMMERS'] = '/opt/web/sites/MISHAP/data/swimmers/swimmers_VOS.json'
pwswimmeets.settings.DATAFILES['TEAMS'] = '/opt/web/sites/MISHAP/data/pwslteams.json'

print "Content-type: application/json"
print
print json.dumps(pwswimmeets.utils.get_data_for_chart(name))
#print json.dumps(pwswimmeets.utils.get_data_for_chart(name,source='rftw'))

