
import rftw
import pwsl
import logging
import re

log = logging.getLogger()

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
    s = pwsl.SwimMeetServices()
    rows = {}
    athletes = s.find_swimmer_by_lname(name)
    athnos = [ r['AthNo'] for r in athletes ]
    for athno in athnos:
        print "athno: %s"%athno
        res = s.get_athlete(athno)
        for event in res['HistoryResults']:
            evt = event['ResultType']
            log.debug("evt: %s"%evt)
            for h in event['History']:
                datatime = h['FinTime']
                mdate = h['MeetDate']
                mdate = mdate[ 0 : mdate.rindex("(") ]
                log.debug("    %s"%mdate)
                if mdate not in rows:
                    rows[mdate] = {}
                rows[mdate][evt] = datatime
    print rows
    return rows

def update_swimmer_list():
    pass

def get_best_time(name,event):
    pass

def gen_time_standards(csvfile=None):
    '''
    Need to get data from somewhere.
    I created a csv from: http://www.pwcweb.com/makos/PWSL_2003_Time_Standards.htm
    '''
    if csvfile is None:
        return None
    import csv
    import json
    import re
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
        #sa = e['PWA']
        #sb = e['PWB']
        ta = [float(r) for r in reversed(e['PWA'].split(':'))]
        if len(ta) > 0:
            sa = ta[0]
        if len(ta) > 1:
            sa = float(sa) + int(ta[1])*60
        tb = [float(r) for r in reversed(e['PWB'].split(':'))]
        if len(tb) is not None:
            sb = tb[0]
        if len(tb) > 1:
            sb = float(sb) + int(tb[1])*60
        e['FinA'] = round(sa,2)
        e['FinB'] = round(sb,2)
    return j

def gen_event_list(meetdb='SwimMeetVOSD'):
    s = pwsl.SwimMeetServices()
    events = s.get_events(meetdb)
    evdata = [ {'event_number':e['EventNumber'],'event_name':e['EventName'].strip()} for e in events ]
    for e in evdata:
        ename = e['event_name']
        m = re.search('(\w+) (\d+-\d+|\d+ & Under) (\d+) Meter (\w[\w\s]+)',ename,re.I)
        if m is None:
            log.error("%s not parseable"%ename)
            continue
        e['sex'] = m.group(1).replace('Boys','Male').replace('Girls','Female')
        e['age'] = m.group(2).replace('10 & Under','9-10')
        e['dist'] = m.group(3)
        e['stroke'] = m.group(4)
        if e['stroke'] == 'Medly':
            e['stroke'] = 'IM'
            e['event_name'] = e['event_name'].replace('Medly','IM').replace('10 & Under','9-10')
    return evdata

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    get_data_for_chart('bianc')

    '''
import pwswimmeets
from pprint import pprint as pp
evdata = pwswimmeets.utils.gen_event_list(meetdb='SwimMeetBLST')
pp(evdata)
    '''

