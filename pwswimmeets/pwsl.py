import json
import requests
import re
import logging

log = logging.getLogger()

class SwimMeetServices(object):

    def __init__(self):
        self.url = 'http://www.pwswimmeets.com/swimmeetservices.asmx'
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.saccessid = '912597'#929721 would this work: 895473
        self.spwd = ''
        self.reporttypes = ['8','10','12','14','18','Free','IM','Back','Breast','Fly']

    def find_swimmer_by_lname(self,slastname,exact=False):
        '''
        returns:
        [ {'AthName': 'Phelps, Michael', 
           'Sex': 'F', 
           'AthNo': '1234', 
           'AthTeamAbbr': 'VOSD', 
           'DOB': None, 
           'HistoryResults': None, 
           'Age': None, 
           'TeamNo': None, 
           'Events': None}
        ]
        DOB, HistoryResults, Age, TeamNo, Events are always None
        '''
        service = 'FindSwimmerByLName'
        data = {'sLastName':slastname}
        res = self._doit(service,data)
        if exact:
            aths = [n for n in res if n['AthName'].lower() == slastname.lower()]
        else:
            aths = [n for n in res if n['AthName'].lower().startswith(slastname.lower())]
        return aths

    def get_athlete(self,athno=None,meetdb='SwimMeet',history='Yes'):
        '''
        returns:
        {'Age': '99',
         'AthName': 'Phelps, Michael',
         'AthNo': '8066',
         'AthTeamAbbr': 'VOSD',
         'DOB': '6/7/2007',
         'Events': '',
         'Sex': 'F',
         'TeamNo': '9999',
         'HistoryResults': [
            {
             'History': [
                {'DisplayTime': None,
                 'FinTime': None,
                 'MeetDate': '07-06-2013(BLST)'}
             ],
             'ResultType': 'Back'
            },
            {
             'History': [
                {'DisplayTime': None,
                 'FinTime': None,
                 'MeetDate': '07-06-2013(BLST)'}
             ],
             'ResultType': 'Breast'
            }
         ]
        }
        'Age' is never right.
        '''
        ## Should note that setting history to 'No' gives a blank response
        ## {"AthNo":null,"AthName":null,etc}
        ## Setting history to anything else (even '') yields the full history result.
        ## Also ... The only working value I have found for MeetDB is 'SwimMeet'
        service = 'GetAthlete'
        if athno is None:
            log.error("No athno given.  Nothing to look up.")
            return None
        data = {'AthNumber':athno, 'MeetDB':meetdb,'History':history}
        res = self._doit(service,data)
        return res

    def get_meet(self,meetdb='SwimMeet',spwd='',saccessid=None):
        service = 'GetMeet'
        if saccessid is None:
            saccessid = self.saccessid
        if spwd is None:
            spwd = self.spwd
        data = {'MeetDB':meetdb,'sAccessID':saccessid,'sPwd':spwd}
        res = self._doit(service,data)
        return res

    def get_events(self,meetdb='SwimMeetVOSD'):
        ## Ok, so meetdb can't just be 'SwimMeet'
        ## It has to include a team abbrev like 'SwimMeetVOSD'
        ## The abbrev is that of the home team.
        ## The output in each case is a list of events that includes 
        ## some data indicating if a record was broken in each event.
        service = 'GetEvents'
        data = {'MeetDB':meetdb}
        res = self._doit(service,data)
        return res

    def get_ind_event(self,eventno=None,meetdb=None):
        service = 'GetIndEvent'
        if eventno is None:
            log.error("Can't get event without EventNumber.")
            return None
        if meetdb is None:
            log.error("Need MeetDB to get events from meet.")
            return None
        data = {'EventNumber':str(eventno),'MeetDB':meetdb}
        res = self._doit(service,data)
        return res

    def get_relay_event(self,eventno=None,meetdb=None):
        service = 'GetRelayEvent'
        if eventno is None:
            log.error("Can't get event without EventNumber.")
            return None
        if meetdb is None:
            log.error("Need MeetDB to get events from meet.")
            return None
        data = {'EventNumber':str(eventno),'MeetDB':meetdb}
        res = self._doit(service,data)
        return res

    def get_report(self,meetdb=None,reporttype=None):
        ## Valid report types:
        ## 8,10,12,14,18,Free,IM,Back,Breast,Fly
        ## However, all of the event reports return a 500!
        if meetdb is None:
            log.error("get_report() requires meetdb.")
            return None
        if reporttype not in self.reporttypes:
            log.error("reporttype is invalid.")
            return None
        data = {'MeetDB':meetdb,'ReportType':reporttype}
        service = 'GetReport'
        res = self._doit(service,data)
        return res

    def hello_world():
        log.error("SwimMeetServices.hello_world() not implemented")
        return None
        service = 'HelloWorld'
        res = self._doit(service,data)
        return res

    def is_ticket_available():
        log.error("SwimMeetServices.is_ticket_available() not implemented")
        return None
        service = 'IsTicketAvailable'
        res = self._doit(service,data)
        return res

    def validate_password():
        log.error("SwimMeetServices.validate_password() not implemented")
        return None
        service = 'ValidatePassword'
        res = self._doit(service,data)
        return res

    def _doit(self,service,data=None,url=None,headers=None):
        if data is None:
            log.error("No data sent to request")
            return None
        if url is None:
            url = self.url + "/" + service
        if headers is None:
            headers = self.headers
        r = requests.post(url,data=json.dumps(data),headers=headers)
        if not r.ok:
            err = r.json()['Message']
            scode = r.status_code
            log.error("Problem getting data (%s): %s"%(scode,err))
            return None
        res = json.loads(r.json()['d'])
        return res


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    ## Put some test stuff in here
