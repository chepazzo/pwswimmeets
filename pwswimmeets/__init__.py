'''
pwswimmeets is a python implementation of the various APIs available to gather 
swim meet results in Prince William County, Virginia.
'''
__version__ = '0.0.1'
__author__ = 'Mike Biacaniello'
__maintainer__ = 'Mike Biacaniello'
__email__ = 'chepazzo@gmail.com'

import pwsl
import rftw
import utils
import settings

import re

__all__ = ['pwsl','rftw','utils','settings']

class Swimmer(object):
    def __init__(self,name):
        names = re.split(',',name)
        self.name = name
        self.lname = names[0]
        self.fname = names[1]
        # PWSL
        self.pwsl_ids = []
        self.sex = None
        self.dob = None
        self.pwsl_team_abbrev = None #AthTeamAbbr
        # RFTW
        self.rftw_ids = []
        self.age = None # swimmer_age
        self.team = None
        self.rftw_team_abbrev = None #team_abbrev
        self.start_date = None
        self.team_name = None
        self.times = {}
        self.add_swimmer(name)

    def get_event_info(self,name):
        '''
        RFTW:
          swimmer_age
          eventname
          meet_id
          points
          seed_time
          finish (placed)
          swimresult (final time)
        PWSL:
          DisplayTime
          FinTime (time in sec.  used for sorting)
          MeetDate
        '''

    def add_swimmer_from_api(self,name):
        athletes = self.s.find_swimmer_by_lname(name,exact=True)
        # sometimes there are multiple results for the same child!
        self.sex = a[0]['Sex']
        self.age = a[0]['Age']
        self.dob = a[0]['DOB']
        self.team = a[0]['AthTeamAbbr']
        #self.athnos = [ a['AthNo'] for a in athletes ]
        for a in athletes:
            athno = a['AthNo']
            self.athnos.append(athno)
            # The assumption has to be that duplicate entries
            # will list different events.  I could do a check here
            # and see if the Sex, Age, DOB, or Team values differed, but 
            # I don't know what I would do with that info.
            results = s.get_athlete(athno)
        return self

if __name__ == '__main__':
    settings.DATAFILES['TIMESTANDARDS'] = './data/timestandards.json'
    settings.DATAFILES['EVENTS'] = './data/timestandards.json'
    settings.DATAFILES['SWIMMERS'] = './data/timestandards.json'
    import json
    stand = json.load(open(settings.DATAFILES['TIMESTANDARDS'],'rb'))
    s = stand[0]
    print "%s %sm %s PWB:%s PWA:%s"%(s['Event'],s['Dist'],s['Stroke'],s['PWB'],s['PWA'])

