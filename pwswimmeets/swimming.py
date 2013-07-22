
import pwsl
import rftw
import utils
import logging
import settings
import datetime
import re
from dateutil import parser as parsedate

log = logging.getLogger(__name__)

SWIMMERS = []
TEAMS = []

def getTeam(tid=None,source=None):
    if tid is None or source is None:
        log.error("You need to specify team_id and source")
        return None
    for t in TEAMS:
        if tid is not None:
            if tid in [ d['id'] for d in t.ids ]:
                return t
    team = Team(tid,source)
    TEAMS.append(team)
    return team

def getSwimmer(sid=None,source=None):
    if sid is None or source is None:
        log.error("You need to specify swimmer_id and source")
        return None
    for s in SWIMMERS:
        if sid in [ d['id'] for d in s.swimmer_ids ]:
            return s
    sw = Swimmer(sid,source)
    SWIMMERS.append(sw)
    return sw

class Team(object):
    def __init__(self,team_id,source):
        self.name = ''
        self.league_name = ''
        self.type = '' # e.g. summer, hs
        self.swimmers = []
        self.ids = [] # {'id':'','source':''}
        self.abbrevs = [] # {'abbrev':'','source':''}
        self.add_id(team_id,source)

    def add_id(self,id=None,source=None):
        if id is None or source is None:
            log.error("Team.add_id():  Both id and source are required")
            return None
        if id in [i['id'] for i in self.ids ]:
            log.error("Id '%s' already exists"%id)
            return self.ids
        self.ids.append({'id':id,'source':source})

    def add_abbrev(self,abbrev=None,source=None):
        if abbrev is None or source is None:
            log.error("Team.add_abbrev():  Both abbrev and source are required")
            return None
        if abbrev in [i['abbrev'] for i in self.abbrevs ]:
            log.error("Abbrev '%s' already exists"%abbrev)
            return self.abbrevs
        self.abbrevs.append({'abbrev':abbrev,'source':source})

    @property
    def json(self):
        obj = {'history':[]}
        for a in ['name','league_name','type','ids','abbrevs']:
            obj[a] = getattr(self,a,None)
        return obj

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
        if stroke_name is None:
            return None
        self.swimmer = swimmer
        self.stroke = stroke_name
        self.history = []

    @property
    def best_time(self):
        history = self.history
        validtimes = [h for h in history if h.fintime is not None]
        if len(validtimes) == 0:
            return None
        btime = min(validtimes, key=lambda x:x.fintime)
        return btime

    @property
    def seasonbest_time(self):
        history = self.history
        season = datetime.datetime.today().year
        validtimes = [h for h in history if h.fintime is not None and h.season == season]
        if len(validtimes) == 0:
            return None
        btime = min(validtimes, key=lambda x:x.fintime)
        return btime

    @property
    def last_time(self):
        history = self.history
        validtimes = [h for h in history if h.fintime is not None]
        if len(validtimes) == 0:
            return None
        btime = sorted(validtimes,key=lambda x:x.date,reverse=True)[0]
        return btime

    @property
    def season_seed(self):
        history = self.history
        season = datetime.datetime.today().year
        validtimes = [h for h in history if h.fintime is not None and h.season == season]
        if len(validtimes) == 0:
            return None
        firsttime = sorted(validtimes,key=lambda x:x.date)[0]
        return firsttime

    @property
    def json(self):
        obj = {'history':[]}
        for a in ['stroke']:#,'best_time','seasonbest_time','last_time','season_seed']:
            obj[a] = getattr(self,a,None)
        for swimtime in self.history:
            obj['history'].append(swimtime.json)
        return obj

class Swimmer(object):
    '''
    Am expecting to get most of this info from rftw.get_meet()
    which returns complete results for a single meet.

    {
     'name':'',     # rftw.get_meet().indswims[].swimmers[].swimmer_name
     'rftw_ids':[], # rftw.get_meet().indswims[].swimmers[].swimmer_id
     'sex':'',      # rftw.get_meet().indswims[].swimmers[].swimmer_gender
     'team': <Team>,
     'strokes':[<Stroke>]
    }
    '''
    def __init__(self,swimmer_id,source):
        self.name = None
        self.lname = None
        self.fname = None
        self.dob = None
        self.swimmer_ids = [] # rftw.swimmer_id
        self.sex = None #rftw.swimmer_gender
        self.age = None #rftw.swimmer_age
        self.team = None
        self.start_date = None
        self.strokes = []
        self.add_swimmer_id(swimmer_id,source)

    def add_swimmer_id(self,id=None,source=None):
        if id is None or source is None:
            log.error("Swimmer.add_swimmer_id():  Both id and source are required")
            return None
        if id in [i['id'] for i in self.swimmer_ids ]:
            log.error("Id '%s' already exists"%id)
            return self.swimmer_ids
        self.swimmer_ids.append({'id':id,'source':source})

    def addSwimTime(self,event_name,**kwargs):
        swtime = SwimTime(self,event_name=event_name,**kwargs)
        stroke_name = '%s %s'%(swtime.event_dist,swtime.event_stroke)
        stroke = self.get_stroke(stroke_name)
        stroke.history.append(swtime)
        return swtime

    def get_stroke(self,stroke_name):
        if not re.match('^\d+\w? [\w\s]+$',stroke_name):
            log.error("Invalid Stroke: '%s'"%stroke_name)
            return None
        strokes = self.strokes
        ss = [ s for s in strokes if s.stroke == stroke_name ]
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

    @property
    def json(self):
        obj = {'strokes':[]}
        for a in ['name','swimmer_ids','dob','sex']:
            obj[a] = getattr(self,a,None)
        obj['team'] = self.team.name
        for stroke in self.strokes:
            obj['strokes'].append(stroke.json)
        return obj

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
        self._pwt = None
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
        if val is None:
            self.date = None
            return None
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
        status = "OK"
        if value is None:
            status = val
        self.status = status
        self.fintime = value
        return value

    @property
    def hmstime(self):
        #print "self.fintime = '%s'"%str(self.fintime)
        return utils.secs2hms(self.fintime)

    @property
    def seedtime(self):
        return self.finseedtime
    @seedtime.setter
    def seedtime(self,val):
        '''
        SwimTime.seedtime setter to parse value and store 
        as float in self.finseedtime
        '''
        value = time2secs(val)
        self.finseedtime = value
        return value

    @property
    def hmsseedtime(self):
        #print "self.finseedtime = '%s'"%str(self.finseedtime)
        return utils.secs2hms(self.finseedtime)

    @property
    def json(self):
        obj = {}
        for a in ['meet_id','status','season','event_name','event_num','time','seedtime','points','place','PWT']:
            obj[a] = getattr(self,a,None)
        obj['meet_date'] = self.meet_date.strftime('%B %d, %Y')
        #obj['PWT'] = self.PWT
        return obj

def time2secs(val):
    value = val ## doing this to preserve the original value for logging at the end.
    if type(value) is int:
        value = float(value)
    elif type(value) is str or type(value) is unicode:
        if not re.match('^[\d\:\.]+$',value):
            return None
        value = utils.hms2secs(value)
    if type(value) is float or value is None:
        return value
    log.error("%s is invalid time type (%s).  Shoud be float, int, str, or None"%(str(val),str(type(val))))
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
