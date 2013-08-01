import re
import os
import json
import datetime
import logging
from dateutil import parser as parsedate

import rftw
import pwsl
import swimming
import settings

log = logging.getLogger(__name__)

PWTIMES = None

def get_data_for_chart(name,source=None):
    """
    formats data for display with Google Charts
    data needs to be grouped by date.
    each col corresponds to an x-axis value
    each row is a collection of y-axis values for a specific x.
    e.g. If you want to draw a horiz line graph (function), 
      then each row would be a new data point on that line.
      Multiple lines means multiple items in the row.

    For a swim meet, this means that each row corresponds to a meet
      and each col corresponds to an event.

    :param name:
        Searches based on name
        Hint:  if you send the string as "mylastname, myfirstname" it will still match
    :param athno:

    :returns:
        something
    """
    if source == 'rftw':
        return _get_data_for_chart_rftw(name)
    else:
        return _get_data_for_chart_local(name)

def _get_data_for_chart_local(name):
    rows = {'events':[],'data':{}}
    if len(swimming.TEAMS) == 0 or len(swimming.SWIMMERS) == 0:
        swimming.loadfromfile()
    swimmerdata = [ s.get_data_for_chart() for s in swimming.SWIMMERS if s.name.lower().startswith(name.lower()) ]
    for s in swimmerdata:
        for e in s['events']:
            if e not in rows['events']:
                rows['events'].append(e)
        for d in s['data']:
            if d not in rows['data']:
                rows['data'][d] = s['data'][d]
    return rows

def _get_data_for_chart_rftw(name):
    rows = {'events':[],'data':{}}
    r = rftw.SwimMeetServices()
    events = r.find_swimmer_history_by_lname(name)
    for h in events:
        ename = h['eventname']
        swimtime = h['swimresult']
        #if swimtime == 'DQ':
        #    continue
        #if swimtime == 'NS':
        #    continue
        #if swimtime == 'DNF':
        #    continue
        fintime = hms2secs(swimtime)
        mdate = h['startdate'].replace('st,',',').replace('nd,',',').replace('th,',',').replace('rd,',',')
        #m = re.search('(\w+) (\d+-\d+|\d+ & Under|\d+ and Under) (\d+)(?: Meter)? (\w[\w\.\s]+)',ename,re.I)
        #ename = ename.replace('10 and Under','9-10').replace('12 and Under','11-12').replace('14 and Under','13-14').replace('18 and Under','15-18')
        #ename = ename.replace('I.M.','IM');
        #ename = ename.replace('and Under','& Under');
        #dist = m.group(3)
        #stroke = m.group(4)
        enametup = normalize_event_name(ename)
        ename = enametup[0]
        dist = enametup[3]
        stroke = enametup[4]
        if stroke.endswith('Relay'):
            continue
        evt = "%s %s"%(dist,stroke)
        PWT = get_pwtime(fintime,ename)
        if evt not in rows['events']:
            rows['events'].append(evt)
        if mdate not in rows['data']:
            rows['data'][mdate] = {'date':mdate}
        rows['data'][mdate][evt] = {'fintime':fintime,'hmstime':swimtime,'PWT':PWT}
    return rows

def normalize_event_name(ename):
    if ename is None:
        return (None,None,None,None,None)
    m = re.search('(\w+) (\d+-\d+|\d+ & Under|\d+ and Under)?\s?(\d+)(?: Meter)? (\w[\w\.\s]+)',ename,re.I)
    if m is None:
        log.error("normalize_event_name('%s'): regex not working"%ename)
        return (None,None,None,None,None)
    sex = m.group(1)
    age = m.group(2)
    dist = m.group(3)
    stroke = m.group(4)
    sex = sex.replace('Male','Boys').replace('Female','Girls')
    if age is not None:
        age = age.replace('10 and Under','9-10').replace('12 and Under','11-12').replace('14 and Under','13-14').replace('18 and Under','15-18')
        age = age.replace('and Under','& Under');
    stroke = stroke.replace('I.M.','IM');
    ename = "%s %s %s Meter %s"%(sex,age,dist,stroke)
    return (ename,sex,age,dist,stroke)

def update_swimmer_list():
    pass

def get_best_times(name,source=None):
    if source == 'rftw':
        return _get_best_times_rftw(name)
    else:
        return _get_best_times_local(name)

def _get_best_times_local(name):
    store = {}
    if len(swimming.TEAMS) == 0 or len(swimming.SWIMMERS) == 0:
        swimming.loadfromfile()
    swimmerdata = [ s.get_best_times() for s in swimming.SWIMMERS if s.name.lower().startswith(name.lower()) ]
    for s in swimmerdata:
        for evt in s:
            e = s[evt]
            if evt not in store:
                store[evt] = e
            else:
                log.debug('multiple swimmer data (%s) with overlapping best time data'%e['name'])
    return [store[evt] for evt in store]

def _get_best_times_rftw(name):
    store = {}
    r = rftw.SwimMeetServices()
    events = r.find_swimmer_history_by_lname(name)
    for h in events:
        ename = h['eventname']
        swimmername = h['swimmer_name']
        swimtime = h['swimresult']
        seedtime = h['seedtime']
        #if swimtime == 'DQ':
        #    continue
        #if swimtime == 'NS':
        #    continue
        #if swimtime == 'DNF':
        #    continue
        fintime = hms2secs(swimtime)
        finseedtime = hms2secs(seedtime)
        mdate = h['startdate'].replace('st,',',').replace('nd,',',').replace('th,',',').replace('rd,',',')
        #m = re.search('(\w+) (\d+-\d+|\d+ & Under|\d+ and Under) (\d+)(?: Meter)? (\w[\w\.\s]+)',ename,re.I)
        #dist = m.group(3)
        #stroke = m.group(4)
        enametup = normalize_event_name(ename)
        ename = enametup[0]
        dist = enametup[3]
        stroke = enametup[4]
        if stroke.endswith('Relay'):
            continue
        evt = "%s %s"%(dist,stroke)
        if evt not in store:
            store[evt] = {'times':[],'res':{'name':swimmername,'event':evt}}
        store[evt]['times'].append({'finseedtime':finseedtime,'fintime':fintime,'date':mdate,'findate':datetime.datetime.strptime(mdate,'%B %d, %Y')})
    for evt in store:
        resultstore = store[evt]['res']
        season = datetime.date.today().year
        ## Look for best time in event
        fintimes = [ t['fintime'] for t in store[evt]['times'] if t['fintime'] is not None ]
        besttime = None
        if len(fintimes)>0:
            besttime = min(fintimes)
        resultstore['best'] = {'fintime':besttime,'hmstime':secs2hms(besttime)}
        ## Look for best time in event this season
        sfintimes = [ t['fintime'] for t in store[evt]['times'] if t['findate'].year == season and t['fintime'] is not None ]
        seasonbesttime = None
        if len(sfintimes)>0:
            seasonbesttime = min(sfintimes)
        resultstore['seasonbest'] ={'fintime':seasonbesttime,'hmstime':secs2hms(seasonbesttime)}
        ## Look for most recent time for event
        sortedtimes = sorted(store[evt]['times'],key=lambda x: x['findate'],reverse=True)
        lasttime = sortedtimes[0]
        lastfintime = lasttime['fintime']
        resultstore['last'] = {'date':lasttime['date'],'fintime':lastfintime,'hmstime':secs2hms(lastfintime)}
        ## Look for penultimate time for event
        ## (expected to be used for seed for 'lasttime')
        prevtime = None
        prevdate = None
        #if len(sortedtimes) > 1:
        #    #prevtime = sortedtimes[1]
        #    prevtime = sortedtimes[1]['fintime']
        #    prevdate = sortedtimes[1]['date']
        #if sortedtimes[0]['finseedtime'] is not None:
        prevtime = sortedtimes[0]['finseedtime']
        resultstore['prev'] = {'date':prevdate,'fintime':prevtime,'hmstime':secs2hms(prevtime)}
        ## Look for season seed time.
        thisyeartimes = [ t for t in reversed(sortedtimes) if t['findate'].year == season ]
        thisyeartime = None
        thisyeardate = None
        if len(thisyeartimes) > 0:
            thisyeartime = thisyeartimes[0]['fintime']
            thisyeardate = thisyeartimes[0]['date']
        resultstore['seed'] = {'date':thisyeardate,'fintime':thisyeartime,'hmstime':secs2hms(thisyeartime)}
    return [ store[evt]['res'] for evt in store ]
    #return [ {'name':swimmername,'event':evt,'besttime':store[evt]['best']} for evt in store ]

def get_team_best(team_name=None,team_abbrev=None):
    ret = {'bystroke':[],'byswimmer':[]}
    if len(swimming.TEAMS) == 0 or len(swimming.SWIMMERS) == 0:
        swimming.loadfromfile()
    team = None
    if team_name is not None:
        team = swimming.getTeam(name=team_name)
    elif team_abbrev is not None:
        team = swimming.getTeam(abbrev=team_abbrev)
    if team is None:
        return None
    for s in swimming.SWIMMERS:
        if s.team is not team:
            continue
        swim_name = s.name
        swim_numbest = s.numbest
        swim_totimp = s.totalimproved
        sres = {
            'name':swim_name,
            'numbest':swim_numbest,
            'totimp':swim_totimp
        }
        ret['byswimmer'].append(sres)
        for stroke in s.strokes:
            numbest = stroke.numbest
            stroke_name = stroke.stroke
            bestst = stroke.seasonbest_time
            if bestst is None:
                continue
            seedst = stroke.seasonseed_time
            finbest = bestst.fintime
            bestdate = bestst.date.strftime('%B %d, %Y')
            finseed = None
            seeddate = None
            if seedst is not None:
                finseed = seedst.fintime
                seeddate = seedst.date.strftime('%B %d, %Y')
                if seedst.finseedtime is not None:
                    finseed = seedst.finseedtime
            imp = stroke.season_improve
            impperc = stroke.season_improve_percent
            impperm = stroke.season_improve_permeter
            res = {
                'stroke':stroke_name,
                'name':swim_name,
                'best':{'date':bestdate,'fintime':finbest,'hmstime':secs2hms(finbest)},
                'seed':{'date':seeddate,'fintime':finseed,'hmstime':secs2hms(finseed)},
                'improve':imp,
                'improveperc':impperc,
                'improveperm':impperm,
                'numbest':numbest
            }
            ret['bystroke'].append(res)
    return ret

def find_meet_results(team_name=None,team_abbrev=None,season=None,meet_date=None,league_abbrev=None):
    if season is None:
        if meet_date is not None:
            season = parsedate.parse(meet_date).year
        else:
            season = datetime.datetime.today().year
    ret = []
    r = rftw.SwimMeetServices()
    res = r.get_meet_results(season=season)
    for m in res:
        if meet_date is not None and parsedate.parse(m['meet_date']) != parsedate.parse(meet_date):
            continue
        if league_abbrev is not None:
            if m['league_abbrev'].strip() != league_abbrev:
                continue
        if team_abbrev is not None:
            if len([ t for t in m['teams'] if t['team_abbrev'] == team_abbrev ]) < 1:
                continue
        if team_name is not None:
            if len([ t for t in m['teams'] if re.search(team_name,t['team_name'],re.I) ]) < 1:
                continue
        ret.append(m)
    return ret

def find_meet_ids(*args,**kwargs):
    '''
    params: 
        team_name=None,
        team_abbrev=None,
        season=None,
        meet_date=None

    returns:
        list of meet_ids sorted by most recent meet
    '''
    meets = find_meet_results(*args,**kwargs)
    sortedmeets = sorted(meets,key=lambda x: parsedate.parse(x['meet_date']),reverse=True)
    return [ {'id':m['meet_id'],'date':m['meet_date']} for m in sortedmeets ]

def find_meets(*args,**kwargs):
    '''
    params: 
        team_name=None,
        team_abbrev=None,
        season=None,
        meet_date=None
    '''
    r = rftw.SwimMeetServices()
    meetids = find_meet_ids(*args,**kwargs)
    if len(meetids) <1:
        return None
    ret = []
    for meetid in meetids:
        res = r.get_meet(meetid=meetid['id'])
        ret.append(res)
    return ret

def get_pwtime(ftime=None,event_name=None):
    if ftime is None:
        log.error("get_pwtime() requires a time to check")
        return None
    if event_name is None:
        log.error("get_pwtime() requires an event name to check")
        return None
    pwtimes = get_time_standards()
    for t in pwtimes:
        if t['event_name'] != event_name:
            continue
        log.debug("Comparing %.2f to PWA:%.2f and PWB:%.2f"%(ftime,t['FinA'],t['FinB']))
        if ftime <= t['FinA']:
            log.debug('    PWA TIME!!!!!')
            return 'A'
        elif ftime <= t['FinB']:
            log.debug('    PWB TIME!!!!!')
            return 'B'
        else:
            return None 
    log.error('get_pwtime(): event_name ("%s") not found in time_standards'%event_name)
    return None

def get_time_standards():
    if PWTIMES is None:
        load_time_standards()
    return PWTIMES

def load_time_standards():
    global PWTIMES
    tsfile = os.path.join(settings.DATAFILEPATH,settings.DATAFILES['TIMESTANDARDS'])
    if tsfile is None:
        log.error("get_time_standards() unable to find DATAFILES['TIMESTANDARDS'] in %s"%tsfile)
        return None
    PWTIMES = json.load(open(tsfile,'rb'))
    return PWTIMES

def gen_teams():
    ## Requiring league to be set in settings file
    ## Otherwise it starts to get complicated and
    ## I'd have to require that the user pass args
    ## for league_id and name and abbrev
    league = settings.LEAGUE.get('name',None)
    league = league.replace(' ','_')
    r = rftw.SwimMeetServices()
    teams = r.get_teams(league_name_link=league)
    for t in teams:
        team = swimming.getTeam(source='rftw',tid=t['team_id'])
        for f in ['division','section','address','contact_info','website']:
            v = t[f]
            setattr(team,f,v)
        team.name = t['team_name']
        team.type = t['team_type']
        team.add_abbrev(t['team_abbrev'],'rftw')
        team.league = settings.LEAGUE
    return None

MEETS = None
def gen_meet_results(team_name=None,team_abbrev=None,season=None,meet_date=None):
    '''
    get meet results from API and store results in Swimmer data structure
    '''
    meets = find_meets(team_name=team_name,team_abbrev=team_abbrev,season=season,meet_date=meet_date)
    MEETS = meets
    log.info("Matched %s meets"%len(meets))
    for meet in meets:
        _gen_meet_results(meet=meet)
    #
def _gen_meet_results(meet=None):
    if meet is None:
        return None
    meet_id = meet['meet_id']
    log.debug("storing meet: %s"%meet_id)
    season = meet['season']
    meet_date = meet['meet_date']
    log.debug("    date:%s"%meet_date)
    #
    for t in meet['teams']:
        tid = t['team_id']
        tn = t['team_name']
        #
        team = swimming.getTeam(tid,'rftw')
        team.name = tn
        log.debug("    team:'%s','%s'"%(t['league_abbrev'],team.name))
    #
    indswims = meet.get('indswims',None)
    if indswims is None:
        return None
    for event in indswims:
        event_name = event['eventname']
        event_num = event['eventnum']
        #
        swimmers = event['swimmers']
        for sw in swimmers:
            rftw_id = sw['swimmer_id']
            name = sw['swimmer_name']
            sex = sw['swimmer_gender']
            #
            rftw_team_id = sw['team_id']
            rftw_team_abbrev = sw['team_abbrev']
            #
            hmstime = sw['swimresult']
            seedtime = sw['seedtime']
            points = sw['points']
            place = sw['finish']
            #
            swimmer = swimming.getSwimmer(rftw_id,'rftw')
            if swimmer.name is None:
                swimmer.name = name
                swimmer.sex = sex
                swimmer.team = swimming.getTeam(rftw_team_id,'rftw')
                swimmer.team.add_abbrev(rftw_team_abbrev,'rftw')
            swimtime = swimmer.addSwimTime(event_name)
            swimtime.meet_id = meet_id
            swimtime.meet_date = meet_date
            #
            swimtime.event = event_name
            swimtime.event_num = event_num
            swimtime.time = hmstime
            swimtime.seedtime = seedtime
            swimtime.points = points
            swimtime.place = place

def gen_meet_result_history(team_name=None,team_abbrev=None,season=None,meet_date=None):
    meet_data = gen_meet_results(team_abbrev=team_abbrev,season='2013')

def gen_time_standards(csvfile=None):
    '''
    Need to get data from somewhere.
    I have yet to find a programatic interface that contains this data.
    I created a csv from: http://www.pwcweb.com/makos/PWSL_2003_Time_Standards.htm
    This function expects a csv file of the format:
    #event_name,sex,age,dist,stroke
    '''
    if csvfile is None:
        return None
    import csv
    d = csv.DictReader(open(csvfile,'rb'))
    j = [row for row in d]
    for e in j:
        ename = e['event_name']
        if ename.startswith('Male'):
            e['sex'] = 'Male'
        elif ename.startswith('Female'):
            e['sex'] = 'Female'
        m = re.search('(\w+) (\d+-\d+|8 & Under)',ename,re.I)
        e['age'] = m.group(2)
        sex = e['sex'].replace('Male','Boys').replace('Female','Girls')
        e['event_name'] = "%s %s %s Meter %s"%(sex,e['age'],e['dist'],e['stroke'])
        #ta = [float(r) for r in reversed(e['PWA'].split(':'))]
        #if len(ta) > 0:
        #    sa = ta[0]
        #if len(ta) > 1:
        #    sa = float(sa) + int(ta[1])*60
        #tb = [float(r) for r in reversed(e['PWB'].split(':'))]
        #if len(tb) is not None:
        #    sb = tb[0]
        #if len(tb) > 1:
        #    sb = float(sb) + int(tb[1])*60
        #e['FinA'] = round(sa,2)
        #e['FinB'] = round(sb,2)
        e['FinA'] = hms2secs(e['PWA'])
        e['FinB'] = hms2secs(e['PWB'])
    return j

def gen_event_list(meetdb='SwimMeetVOSD'):
    '''
    This will grab the latest swim meet data from pwsl
    and extract the event names into a data structure.
    This can be useful later for referencing event numbers to 
    request data from the services.
    '''
    s = pwsl.SwimMeetServices()
    events = s.get_events(meetdb)
    evdata = [ {'event_number':e['EventNumber'],'event_name':e['EventName'].strip()} for e in events ]
    for e in evdata:
        ename = e['event_name'].replace('Medly','Medley')
        m = re.search('(\w+) (\d+-\d+|\d+ & Under) (\d+) Meter (\w[\w\s]+)',ename,re.I)
        if m is None:
            log.error("%s not parseable"%ename)
            continue
        e['sex'] = m.group(1).replace('Boys','Male').replace('Girls','Female')
        e['age'] = m.group(2).replace('10 & Under','9-10')
        e['dist'] = m.group(3)
        e['stroke'] = m.group(4)
        if e['stroke'] == 'Medley':
            e['stroke'] = 'IM'
            e['event_name'] = e['event_name'].replace('Medley','IM').replace('10 & Under','9-10')
    return evdata

def hms2secs(hms=None):
    '''
    hms is expected to be a string of the format hh:mm:ss.ss
    '''
    if hms is None:
        return None
    if not re.match('^[\d\:\.]+$',hms):
        log.error("'%s' not in h:m:s format"%hms)
        return None
    m = [float(r) for r in reversed(hms.split(':'))]
    if len(m) > 0:
        s = m[0]
    if len(m) > 1:
        s = float(s) + int(m[1])*60
    return round(s,2)

def secs2hms(secs=None):
    '''
    secs is expected to be a float
    '''
    if secs is None:
        return None
    if not re.match('^[\d\.]+$',str(secs)):
        log.error("'%s' not a number!"%str(secs))
    m,s = divmod(secs,60)
    h,m = divmod(m,60)
    s = round(s,2)
    val = "%d:%02d:%05.2f"%(h,m,s)
    if int(secs) < 60:
        val = "%.2f"%s
    elif int(secs) < 3600:
        val = "%d:%05.2f"%(m,s)
    return val
    #return "%d:%05.2f"%(m,round(s,2))

if __name__ == '__main__':
    #log.setLevel(logging.DEBUG)
    #log.addHandler(logging.StreamHandler())
    #get_data_for_chart('bianc')
    #print get_best_times('phelps, michael')
    #import pwswimmeets
    import logging
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    from pprint import pprint as pp
    #for season in range(2009,2013+1):
    for season in [2013]:
        meet_data = gen_meet_results(team_abbrev='VOS',season=season)
    phelps = [ s.json for s in swimming.SWIMMERS if s.name.startswith('Phelps, Michael') ][0]
    pp(phelps)
    #evdata = pwswimmeets.utils.gen_event_list(meetdb='SwimMeetBLST')
    #evdata = pwswimmeets.utils.get_data_for_chart('phelps, michael')
    #pp(evdata)

'''
import pwswimmeets
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
from pprint import pprint as pp
meet_data = pwswimmeets.utils.gen_meet_results(team_abbrev='VOS',meet_date='7/13/2013')
pp(meet_data)
#evdata = pwswimmeets.utils.gen_event_list(meetdb='SwimMeetBLST')
#evdata = pwswimmeets.utils.get_data_for_chart('phelps, michael')
#pp(evdata)
'''
