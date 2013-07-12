import rftw
import pwsl
import logging
import re
import json
import datetime
from . import settings

log = logging.getLogger()

PWTIMES = None

def get_data_for_chart(name):
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
    rows = {'events':[],'data':{}}
    r = rftw.SwimMeetServices()
    events = r.find_swimmer_history_by_lname(name)
    for h in events:
        ename = h['eventname']
        swimtime = h['swimresult']
        if swimtime == 'DQ':
            continue
        if swimtime == 'NS':
            continue
        if swimtime == 'DNF':
            continue
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
    m = re.search('(\w+) (\d+-\d+|\d+ & Under|\d+ and Under) (\d+)(?: Meter)? (\w[\w\.\s]+)',ename,re.I)
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

def get_best_time(name,event):
    pass

def get_best_times(name):
    store = {}
    r = rftw.SwimMeetServices()
    events = r.find_swimmer_history_by_lname(name)
    for h in events:
        ename = h['eventname']
        swimmername = h['swimmer_name']
        swimtime = h['swimresult']
        if swimtime == 'DQ':
            continue
        if swimtime == 'NS':
            continue
        if swimtime == 'DNF':
            continue
        fintime = hms2secs(swimtime)
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
        store[evt]['times'].append({'fintime':fintime,'date':mdate,'findate':datetime.datetime.strptime(mdate,'%B %d, %Y')})
    for evt in store:
        resultstore = store[evt]['res']
        season = datetime.date.today().year
        ## Look for best time in event
        fintimes = [ t['fintime'] for t in store[evt]['times'] ]
        besttime = min(fintimes)
        resultstore['best'] = {'fintime':besttime,'hmstime':secs2hms(besttime)}
        ## Look for best time in event this season
        sfintimes = [ t['fintime'] for t in store[evt]['times'] if t['findate'].year == season ]
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
        if len(sortedtimes) > 1:
            #prevtime = sortedtimes[1]
            prevtime = sortedtimes[1]['fintime']
            prevdate = sortedtimes[1]['date']
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

def get_pwtime(ftime=None,event=None):
    if ftime is None:
        log.error("get_pwtime() requires a time to check")
        return None
    if event is None:
        log.error("get_pwtime() requires an event name to check")
        return None
    pwtimes = get_time_standards()
    for t in pwtimes:
        if t['event_name'] != event:
            continue
        log.debug("Comparing %.2f to PWA:%.2f and PWB:%.2f"%(ftime,t['FinA'],t['FinB']))
        if ftime <= t['FinA']:
            log.debug('    PWA TIME!!!!!',event)
            return 'A'
        elif ftime <= t['FinB']:
            log.debug('    PWB TIME!!!!!',event)
            return 'B'
        else:
            return None 
    log.error('get_pwtime(): event_name not found in time_standards')
    return None

def get_time_standards():
    if PWTIMES is None:
        load_time_standards()
    return PWTIMES

def load_time_standards():
    global PWTIMES
    tsfile = settings.DATAFILES['TIMESTANDARDS']
    if tsfile is None:
        log.error("get_time_standards() unable to find DATAFILES['TIMESTANDARDS']")
        return None
    PWTIMES = json.load(open(tsfile,'rb'))
    return PWTIMES

def gen_time_standards(csvfile=None):
    '''
    Need to get data from somewhere.
    I created a csv from: http://www.pwcweb.com/makos/PWSL_2003_Time_Standards.htm
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
    if hms is None:
        return None
    m = [float(r) for r in reversed(hms.split(':'))]
    if len(m) > 0:
        s = m[0]
    if len(m) > 1:
        s = float(s) + int(m[1])*60
    return round(s,2)

def secs2hms(secs=None):
    if secs is None:
        return None
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
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    #get_data_for_chart('bianc')
    print get_best_times('phelps, michael')
    '''
import pwswimmeets
from pprint import pprint as pp
#evdata = pwswimmeets.utils.gen_event_list(meetdb='SwimMeetBLST')
evdata = pwswimmeets.utils.get_data_for_chart('phelps, michael')
pp(evdata)
    '''

