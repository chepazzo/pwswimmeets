'''
pwswimmeets is a python implementation of the various APIs available to gather 
swim meet results in Prince William County, Virginia.

This package simplifies the collection of data from reachthewall.com and pwswimmeets.com.

See http://www.pwswimmeets.com/swimmeetservices.asmx for full pwsm cmd reference.

cmd ref for reachthewall.com has been pieced together with the help of FireBug while browsing the site.
'''


__version__ = '0.0.1'
__author__ = 'Mike Biacaniello'
__maintainer__ = 'Mike Biacaniello'
__email__ = 'chepazzo@gmail.com'
__url__ = 'https://github.com/chepazzo/pwswimmeets'
__shortdesc__ = 'API for swimmer data for Prince William County, Virginia.'
import pwsl
import rftw
import utils
import settings

import re

__all__ = ['pwsl','rftw','utils','settings']

class Swimmer(object):
    '''
    Am expecting to get most of this info from rftw.get_meet()
    which returns complete results for a single meet.

    {
     'name':'',     # rftw.get_meet().indswims[].swimmers[].swimmer_name
     'rftw_ids':[], # rftw.get_meet().indswims[].swimmers[].swimmer_id
     'sex':'',      # rftw.get_meet().indswims[].swimmers[].swimmer_gender
     'team_ids':[{'id':'','source':'rftw'}],         # rftw.get_meet().indswims[].swimmers[].team_id
     'team_abbrevs':[{'abbrev':'','source':'rftw'}], # rftw.get_meet().indswims[].swimmers[].team_abbrev
     'times':{
        '25 fly':{
             ## should these just ref the history index?
            'best':'',             # calc'd: self.best_time()
            'seasonbest':'',       # calc'd: self.seasibbest_time()
            'recent':'',           # calc'd: self.recent_time()
            'stroke':'',           # utils.normalize_event_name(rftw.get_meet().indswims[].eventname)[3,4]
            'history':[{
                'event_name':'',   # utils.normalize_event_name(rftw.get_meet().indswims[].eventname)[0]
                'event_num':'',    # rftw.get_meet().indswims[].eventnum
                'meet_id':'',      # rftw.get_meet().meet_id
                'season':'',       # rftw.get_meet().season
                'date':'',         # rftw.get_meet().meet_date
                'hmstime':'',      # rftw.get_meet().indswims[].swimmers[].swimresult
                'fintime':'',      # rftw.get_meet().indswims[].swimmers[].swimtime_sort
                'hmsseedtime':'',  # rftw.get_meet().indswims[].swimmers[].seedtime
                'points':'',       # rftw.get_meet().indswims[].swimmers[].points
                'place':'',        # rftw.get_meet().indswims[].swimmers[].finish
                'PWT':''           # calc'd from utils.get_pwtime(fintime,event_name)
            }]
        }
     }
    }
    '''
    SWIMMERS = []
    def __init__(self,name):
        if len([a for a in Swimmer.SWIMMERS if a.name == name]) == 0:
            Swimmer.SWIMMERS.append(self)
        names = re.split(',\s?',name)
        self.name = name
        self.lname = names[0]
        self.fname = names[1]
        # PWSL
        self.pwsl_ids = []
        self.dob = None
        self.pwsl_team_abbrev = None #AthTeamAbbr
        # RFTW
        self.rftw_ids = [] # swimmer_id
        self.sex = None # swimmer_gender
        self.age = None # swimmer_age
        self.team = None
        self.team_id = None # team_id
        self.rftw_team_abbrev = None #team_abbrev
        self.start_date = None
        self.team_name = None
        self.times = {}
        #self.add_swimmer(name)
        #Swimmer.SWIMMERS.append(self)

    def best_time(self,stroke):
        history = self.times[stroke]['history']
        btime = min(history, key=lambda x:x['fintime'])
        return btime

    def seasonbest_time(self,stroke):
        history = self.times[stroke]['history']
        season = datetime.datetime.today().year
        btime = min([h for h in history if h['season'] == season], key=lambda x:x['fintime'])
        return btime

    def last_time(self,stroke):
        history = self.times[stroke]['history']
        btime = sorted([h for h in history],key=lambda x:parsedate.parse(x['date']),reverse=True)[0]
        return btime

    def season_seed(self,stroke):
        history = self.times[stroke]['history']
        season = datetime.datetime.today().year
        firsttime = sorted([h for h in history if h['season'] == season],key=lambda x:parsedate.parse(x['date']))[0]
        return btime

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
          meet_date
        CALCULATED:
          FinTime (time in sec.  used for sorting)
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

    ## Class Methods ##
    def get_swimmers_by_name(name):
        return [a for a in Swimmer.SWIMMERS if a.name == name]

if __name__ == '__main__':
    settings.DATAFILES['TIMESTANDARDS'] = './data/timestandards.json'
    settings.DATAFILES['EVENTS'] = './data/timestandards.json'
    settings.DATAFILES['SWIMMERS'] = './data/timestandards.json'
    import json
    stand = json.load(open(settings.DATAFILES['TIMESTANDARDS'],'rb'))
    s = stand[0]
    print "%s %sm %s PWB:%s PWA:%s"%(s['Event'],s['Dist'],s['Stroke'],s['PWB'],s['PWA'])

