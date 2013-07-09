
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

def gen_event_list(meetdb='SwimMeetVOSD'):
    s = pwsl.SwimMeetServices()
    events = s.get_events(meetdb)
    evdata = [ {'event_number':e['EventNumber'],'event_name':e['EventName'].strip()} for e in events ]
    for e in evdata:
        '''Boys 13-14 50 Meter Fly'''
        ename = e['event_name']
        m = re.search('(\w+) (\d+-\d+|8 & Under) (\d+) Meter (\w+)',ename,re.I)
        if m is None:
            log.error("%s not parseable"%ename)
            continue
        e['sex'] = m.group(1)
        e['age'] = m.group(2)
        e['dist'] = m.group(3)
        e['stroke'] = m.group(4)
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

