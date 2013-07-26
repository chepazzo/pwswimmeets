
import json
import re
import requests
import urllib
import logging
import datetime

log = logging.getLogger()

class SwimMeetServices(object):

    def __init__(self):
        self.url = 'http://www.reachforthewall.com/wp-content/themes/rftw/json.php'
        self.urlss = 'http://wiki.reachforthewall.com/skins/common/swimsearch.php'
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def get_teams(self,league_name_link=None):
        '''
        returns:
        [
         {"team_id":"189",
          "division":"Green",
          "section":"",
          "team_name":"Virginia Oaks Sea Devils",
          "team_shortname":"Virginia Oaks Sea Devils",
          "team_abbrev":"VOS",
          "team_abbrev_too":"VOS",
          "team_type":"Summer",
          "team_name_link":"Virginia_Oaks_Sea_Devils",
          "address":"7980 Virginia Oaks Dr. Gainesville, VA 20155",
          "contact_info":"(703) 753-0497",
          "website":"http://www.swimvaoaks.com/"}
        ]
        '''
        controller = 'teams'
        if league_name_link is None:
            log.error("Must specify a league name.")
            return None
        data = {'ln':league_name_link}
        res = self._doit(controller,data=data)
        return res

    def get_team_info(self,team_name_link=None,season=None):
        '''
        returns:
        {"teamabout":[
         {"team_id":"189",
          "league_id":"5",
          "division":"Green",
          "team_name":"Virginia Oaks Sea Devils",
          "team_abbrev":"VOS",
          "team_shortname":"Virginia Oaks Sea Devils",
          "team_name_link":"Virginia_Oaks_Sea_Devils",
          "team_address":"7980 Virginia Oaks Dr. Gainesville, VA 20155",
          "contact_info":"(703) 753-0497",
          "website":"http://www.swimvaoaks.com/",
          "league_name":"Prince William Swim League ",
          "league_name_link":"Prince_William_Swim_League",
          "league_website":""}
         ]
        }
        '''
        controller = 'team_info'
        if team_name_link is None:
            log.error("Must specify a team name link.")
            return None
        if season is None:
            season = datetime.datetime.today().year
        data = {'team_name_link':team_name_link,'season':season}
        res = self._doit(controller,data=data)
        return res

    def get_swimmer_history(self,sid):
        '''
        returns:
        [
         {"team_name_link": "Virginia_Oaks_Sea_Devils",
          "startdate": "July 6th, 2013",
          "finish": "",
          "seedtime": "",
          "swimmer_name": "Phelps, Michael",
          "season": "2013",
          "swimresult": "1:22.87",
          "eventname": "Girls 12 and Under 100 Free Relay",
          "team_abbrev": "VOS",
          "swimmer_id": "Phelps,Michael259350000",
          "points": "",
          "meet_id": "6319",
          "swimmer_age": "12",
          "league_abbrev": "PWSL ",
          "league_name": "Prince William Swim League ",
          "team_name": "Virginia Oaks Sea Devils",
          "league_name_link": "Prince_William_Swim_League",
          "hsclass": "",
          "team_type": "Summer"}
        ]
        '''
        controller = 'swimmer'
        if sid is None:
            log.error("Must specify a swimmer id.")
            return None
        data = {'sid':sid}
        res = self._doit(controller,data=data)
        return res

    def get_meet_results(self,season=None,ltype=None):
        '''
        returns:
        [
         {"meet_id":"5913",
          "season":"2013",
          "league_id":"4",
          "division":"",
          "meet_date":"2013-06-14",
          "league_name":"Prince-Mont Swim League ",
          "league_abbrev":"PMSL ",
          "league_name_link":"Prince-Mont_Swim_League",
          "pool":"Severn Crossing Swim Team",
          "pool_abbrev":null,
          "meet_type":"Dual Meet",
          "meet_title":"",
          "meet_date_display":"6/14/2013",
          "teams":[
             {"team_name":"Indian Head Swim Team",
              "team_shortname":"Indian Head",
              "team_abbrev":"IH",
              "team_abbrev_too":"IH",
              "team_type":"Summer",
              "team_name_link":"Indian_Head_Swim_Team",
              "points_scored":"262.000",
              "team_id":"141"},
             {"team_name":"Severn Crossing Swim Team",
              "team_shortname":"Severn Crossing",
              "team_abbrev":"SX",
              "team_abbrev_too":"SX",
              "team_type":"Summer",
              "team_name_link":"Severn_Crossing_Swim_Team",
              "points_scored":"280.000",
              "team_id":"155"}
          ]}
        ]
        '''
        controller = 'meet_results'
        if ltype is None:
            ltype = 'summer'
        if season is None:
            season = datetime.datetime.today().year
        data = {'s':season,'lt':ltype}
        res = self._doit(controller,data=data)
        if res is None:
            log.error("get_meet_results(ltype='%s',season='%s') yielded no data."%(ltype,season))
        return res

    def get_meet(self,meetid=None,result='meet'):
        '''
        returns:
        {'boxscoretype': 'complete',
         'season': '2013',
         'team_type': 'summer',
         'course': 'Meters',
         'division': '',
         'meet_date': '2013-07-06',
         'meet_id': '6319',
         'meet_title': '',
         'meet_type': 'Dual Meet',
         'pool': 'Ben Lomond Flying Ducks',
         'pool_abbrev': None,
         'teams': [
            {'league_abbrev': 'PWSL ',
             'league_id': '5',
             'league_name': 'Prince William Swim League ',
             'league_name_link': 'Prince_William_Swim_League',
             'points_scored': '2,239.0',
             'swimtime_unit': 'S',
             'team_abbrev': 'BLS',
             'team_abbrev_too': 'BLS',
             'team_id': '169',
             'team_meet_id': '18110',
             'team_name': 'Ben Lomond Flying Ducks',
             'team_name_link': 'Ben_Lomond_Flying_Ducks',
             'team_shortname': 'Ben Lomond',
             'total_results': '677'}
         ],
         'boxscore': [
            {'eventname': 'Totals  ',
             'teams': [
                {'points': '2,239.0',
                 'team_id': '169',
                 'team_name': 'Ben Lomond Flying Ducks'},
                {'points': '2,649.0',
                 'team_id': '189',
                 'team_name': 'Virginia Oaks Sea Devils'}
             ]}
         ],
         'indswims': [
            {'eventname': 'Boys 8 and Under 25 Free',
             'eventnum': '10',
             'swimmers': [
                {'finish': '1',
                 'hsclass': '',
                 'points': '13.000',
                 'seedtime': '20.78',
                 'status': '',
                 'swimmer_age': '7',
                 'swimmer_gender': 'M',
                 'swimmer_id': 'Phelps,Michael292775000',
                 'swimmer_name': 'Phelps, Michael',
                 'swimresult': '18.79',
                 'swimtime_sort': '18.790',
                 'swimtime_unit': 'S',
                 'team_abbrev': 'VOS',
                 'team_id': '189'}
            ]}
         ],
         'relays': [
            {'eventname': 'Mixed 8 and Under 100 Medley Relay',
             'eventnum': '1',
             'teams': [
                {'points': '47.000',
                 'relay_team': 'B',
                 'seedtime': '1:48.35',
                 'swimmers': [
                    {'hsclass': '',
                     'swimmer_age': '7',
                     'swimmer_id': 'Phelps,Michael292320000',
                     'swimmer_name': 'Phelps, Michael',
                     'swimorder': '1'}
                 ],
                 'swimresult': '1:51.94',
                 'swimtime_sort': '111.940',
                 'swimtime_unit': 'S',
                 'team_abbrev': 'VOS',
                 'team_id': '189'}
            ]}
         ],
         'dives': []}
        '''
        ## Not sure what 'results' can be other than 'meet'
        controller = 'meet'
        if meetid is None:
            log.error('get_meet() requires a meetid.')
            return None
        data = {'meetId':meetid,'result':result}
        res = self._doit(controller,data=data)
        if res is None:
            log.error("get_meet(meetid='%s',result='%s') yielded no data."%(meetid,result))
        return res

    def get_superwinners(self,ltype='summer',team_name_link=None,season=None):
        '''
        returns:
        [
         {"meet_id":"6342",
          "league_abbrev":"PWSL ",
          "team_id":"189",
          "team_abbrev":"VOS",
          "meet_date":"7/20/2013",
          "swimmer_name":"Phelps, Michael",
          "swimmer_age":"9",
          "swimmer_id":"Phelps,Michael279317500",
          "swimmer_gender":"F",
          "season":"2013",
          "hsclass":"",
          "wins":"3",
          "races":"3",
          "total_points":"39.000"}
        ]
        '''
        controller = 'superwinners'
        if team_name_link is None:
            log.error("Must specify a team name link.")
            return None
        if season is None:
            season = datetime.datetime.today().year
        data = {'tnl':team_name_link,'y':season,'lt':ltype}
        res = self._doit(controller,data=data)
        return res

    def get_team_sked(self,team_name_link=None,season=None):
        '''
        returns:
        {'teamabout':<team_info>,
         'sked':[
          {"meet_id":"5897",
           "season":"2013",
           "division":"Green",
           "meet_date":"6/15/2013",
           "pool":"Lake Manassas Blue Dolphins",
           "pool_abbrev":"",
           "meet_type":"Dual Meet",
           "teams":[
            {"team_name":"Virginia Oaks Sea Devils",
             "team_shortname":"Virginia Oaks Sea Devils",
             "team_abbrev":"VOS",
             "team_abbrev_too":"VOS",
             "team_type":"Summer",
             "team_name_link":"Virginia_Oaks_Sea_Devils",
             "points_scored":"2604.500",
             "team_id":"189"}
           ]}
         ]
        }
        '''
        controller = 'team_sked'
        if team_name_link is None:
            log.error("Must specify a team name link.")
            return None
        if season is None:
            season = datetime.datetime.today().year
        data = {'team_name_link':team_name_link,'season':season}
        res = self._doit(controller,data=data)
        return res

    def get_seasons(self):
        '''
        returns:
        {"hs":["2012-13","2011-12","2010-11","2009-10"],
         "high school":["2012-13","2011-12","2010-11","2009-10"],
         "summer":["2013","2013","2012","2011","2010","2009","2008"]}
        '''
        controller = 'seasons'
        data = {}
        res = self._doit(controller,data=data)
        return res

    def find_swimmer_history_by_lname(self,lname):
        '''
        returns same structure as get_swimmer_history
        '''
        controller = 'swimmer'
        if lname is None:
            log.error("Must specify part of a name to search.")
            return None
        data = {'sn':lname}
        res = self._doit(controller,data=data)
        if res == None:
            return None
        aths = [n for n in res if n['swimmer_name'].lower().startswith(lname.lower())]
        return aths

    def find_swimmer_by_lname(self,lname):
        '''
        returns:
        [
         {"link": "http://wiki.reachforthewall.com/Results_Statistics/Swimmer_Results?swimmerId=Phelps,Michael259350000",
          "display": "Phelps, Michael"}
        ]
        '''
        res = self._doit_swimsearch(lname)
        if res == None:
            return None
        aths = [n for n in res if n['display'].lower().startswith(lname.lower())]
        return aths

    def _doit(self,controller,data=None,url=None,headers=None):
        if data is None:
            log.error("No data sent to request")
            return None
        if url is None:
            url = self.url + "?" + controller
        if headers is None:
            headers = self.headers
        data['callback'] = 'a'
        datastr = urllib.urlencode(data)
        log.debug("fetching %s"%url+"&"+datastr)
        r = requests.get(url+"&"+datastr)
        if not r.ok:
            err = r.text
            scode = r.status_code
            log.error("Problem getting data (%s): %s"%(scode,err))
            return None
        jsonp = r.text
        apijson = jsonp[ jsonp.index("(")+1 : jsonp.rindex(")") ]
        res = json.loads(apijson)
        if 'error' in res:
            err = res['error']
            log.error("Problem getting data: %s"%err)
            return None
        return res

    def _doit_swimsearch(self,query=None,url=None,headers=None):
        if query is None:
            log.error("No data sent to request")
            return None
        if url is None:
            url = self.urlss
        if headers is None:
            headers = self.headers
        log.debug("fetching %s"%url+"?q="+query)
        r = requests.get(url+"?q="+query)
        if not r.ok:
            err = r.text
            scode = r.status_code
            log.error("Problem getting data (%s): %s"%(scode,err))
            return None
        res = r.json()
        return res

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler())
    s = SwimMeetServices()
    lname = 'bianc'
    print "find_swimmer_by_lname(%s)"%lname
    r = s.find_swimmer_by_lname(lname)
    print json.dumps(r[0])
    if r is not None:
        for i in r:
            print '    '+i['display']
    print "find_swimmer_history_by_lname(%s)"%lname
    r = s.find_swimmer_history_by_lname('phelps, michael')
    print json.dumps(r[0])
    if r is not None:
        print "    Found %s times!"%len(r)
    for a in r:
        print "    %s:%s"%(a['startdate'],a['eventname'])

