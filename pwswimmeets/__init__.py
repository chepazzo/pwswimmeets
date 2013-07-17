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
import logging
import settings

import re
from dateutil import parser as parsedate

__all__ = ['pwsl','rftw','utils','settings']

log = logging.getLogger(__name__)

SWIMMERS = []

def getSwimmer(name,*args,**kwargs):
    for s in SWIMMERS:
        if s.name == name:
            return s
    return Swimmer(name,*args,**kwargs)

class Stroke(object):
    def __init__(self,swimmer,stroke_name=None):
        '''
        {
         'stroke':''            # utils.normalize_event_name(rftw.get_meet().indswims[].eventname)[3,4]
         'history':[<SwimTime>]
        }
        '''
        if swimmer.__class__ is not Swimmer:
            return None
        if stroke is None:
            return None
        self.swimmer = swimmer
        self.stroke = stroke_name

    @property
    def best_time(self,stroke):
        history = self.history
        btime = min(history, key=lambda x:x.fintime)
        return btime

    @property
    def seasonbest_time(self,stroke):
        history = self.history
        season = datetime.datetime.today().year
        btime = min([h for h in history if h.season == season], key=lambda x:x.fintime)
        return btime

    @property
    def last_time(self,stroke):
        history = self.history
        btime = sorted([h for h in history],key=lambda x:x.date,reverse=True)[0]
        return btime

    @property
    def season_seed(self,stroke):
        history = self.history
        season = datetime.datetime.today().year
        firsttime = sorted([h for h in history if h.season == season],key=lambda x:x.date)[0]
        return btime

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
     'strokes':[
            {'stroke':''            # utils.normalize_event_name(rftw.get_meet().indswims[].eventname)[3,4]
             'history':[<SwimTime>],
              ## should these just ref the history index?
             'best':'',             # calc'd: self.best_time()
             'seasonbest':'',       # calc'd: self.seasonbest_time()
             'recent':''            # calc'd: self.recent_time()
            }
     ]
    }
    '''
    def __init__(self,name):
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

    def get_stroke(self,stroke_name):
        if not re.match('^\d+\w? [\w\s]+$',stroke_name):
            log.error("Invalid Stroke: '%s'"%stroke_name)
            return None
        strokes = self.strokes
        ss = [ s for s in strokes if s.stroke_name == stroke_name ]
        stroke = None
        if len(ss) != 0:
            stroke = ss[0]
        else:
            stroke = Stroke(self,stroke_name)
            self.strokes.append(stroke)
        if stroke.__class__ is not Stroke:
            log.error("Unable to find or create stroke: '%s'"%stroke_name)
            return None
        return stroke

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
        return [a for a in SWIMMERS if a.name == name]

    ## Defining SwimTime class here to make it obvious that a Swimmer instance is expected to be passed.
    class SwimTime(object):
        '''
        {
         'meet_id':'',      # rftw.get_meet().meet_id
         'season':'',       # rftw.get_meet().season
         'meet_date':'',    # rftw.get_meet().meet_date
         'event':'',        # rftw.get_meet().indswims[].eventname
         'event_num':'',    # rftw.get_meet().indswims[].eventnum
         'time':'',         # rftw.get_meet().indswims[].swimmers[].swimtime_sort
         'seedtime':'',     # rftw.get_meet().indswims[].swimmers[].seedtime (cald'd to fintime)
         'points':'',       # rftw.get_meet().indswims[].swimmers[].points
         'place':''         # rftw.get_meet().indswims[].swimmers[].finish
        }
        '''
        def __init__(self,swimmer,meet_id=None,meet_date=None,season=None,
                     event_name=None,event_num=None,
                     time=None,seedtime=None,points=None,place=None):
            if swimmer.__class__ is not Swimmer:
                return None
            self.swimmer = swimmer
            self.meet_id = meet_id
            self.meet_date = meet_date
            self.season = season
            self.event = event_name
            self.event_num = event_num
            self.time = time
            self.seedtime = seedtime
            self.points = points
            self.place = place

        @property
        def PWT(self):
            if self._pwt is None:
                en = self.event_name
                ft = self.fintime
                if en is not None and ft is not None:
                    self._pwt = utils.get_pwtime(ft,en)
            return self._pwt

        ## Parse event_name into component parts
        @property
        def event(self):
            return self._event
        @event.setter
        def event(self,value):
            '''
            (sex,age,distance,stroke)
            '''
            self._event = utils.normalize_event_name(value)
        @property
        def event_name(self):
            return self.event[0]
        @property
        def event_sex(self):
            return self.event[1]
        @property
        def event_age(self):
            return self.event[2]
        @property
        def event_dist(self):
            return self.event[3]
        @property
        def event_stroke(self):
            return self.event[4]
        @property
        def stroke(self):
            dist = self.event[3]
            stroke = self.event[4]
            return "%s %s"%(dist,stroke)

        @property
        def meet_date(self):
            return self.date
        @meet_date.setter
        def meet_date(self,val):
            self.date = parsedate.parse(val)
            if self.season is None:
                self.season = self.date.year

        @property
        def time(self):
            return self.fintime
        @time.setter
        def time(self,val):
            '''
            SwimTime.time setter to parse value and store 
            as float in self.fintime
            '''
            value = time2secs(val)
            self.fintime = value
            return value

        @property
        def hmstime(self):
            return utils.secs2hms(self.fintime)

        @property
        def seedtime(self):
            return self.finseedtime
        @seedtime.setter
        def seedtime(self):
            '''
            SwimTime.seedtime setter to parse value and store 
            as float in self.finseedtime
            '''
            value = time2secs(val)
            self.finseedtime = value
            return value

        @property
        def hmsseedtime(self):
            return utils.secs2hms(self.finseedtime)

def time2secs(val):
    value = val ## doing this to preserve the original value for logging at the end.
    if type(value) is int:
        value = float(value)
    elif type(value) is str:
        value = utils.hms2secs(value)
    if type(value) is float or value is None:
        return value
    log.error("%s is invalid time type.  Shoud be float, int, str, or None"%str(val))
    return None

if __name__ == '__main__':
    settings.DATAFILES['TIMESTANDARDS'] = './data/timestandards.json'
    settings.DATAFILES['EVENTS'] = './data/timestandards.json'
    settings.DATAFILES['SWIMMERS'] = './data/timestandards.json'
    log.setLevel(logging.DEBUG)
    import json
    stand = json.load(open(settings.DATAFILES['TIMESTANDARDS'],'rb'))
    s = stand[0]
    print "%s %sm %s PWB:%s PWA:%s"%(s['Event'],s['Dist'],s['Stroke'],s['PWB'],s['PWA'])

