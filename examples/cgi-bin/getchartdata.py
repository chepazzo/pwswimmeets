#!/usr/bin/env python

import pwswimmeets
import cgi
import json

form = cgi.FieldStorage()
name = form.getvalue("name", None)

print "Content-type: application/json"
print
print json.dumps(pwswimmeets.utils.get_data_for_chart(name))
