
import json
import re
import requests
import urllib
import logging

log = logging.getLogger()

class SwimMeetServices(object):

    def __init__(self):
        self.url = 'http://www.reachforthewall.com/wp-content/themes/rftw/json.php'
        self.urlss = 'http://wiki.reachforthewall.com/skins/common/swimsearch.php'
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

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
        if sid is None:
            log.error("Must specify a swimmer id.")
            return None
        data = {'sid':sid}
        res = self._doit('swimmer',data=data)
        return res

    def find_swimmer_history_by_lname(self,lname):
        '''
        returns same structure as get_swimmer_history
        '''
        if lname is None:
            log.error("Must specify part of a name to search.")
            return None
        data = {'sn':lname}
        res = self._doit('swimmer',data=data)
        if res == None:
            return None
        aths = [n for n in res if n['swimmer_name'].lower().startswith(lname.lower())]
        return res

    def find_swimmer_by_lname(self,lname):
        '''
        returns:
        [
         {"link": "http://wiki.reachforthewall.com/Results_Statistics/Swimmer_Results?swimmerId=Phelps,Michael259350000",
          "display": "Biancaniello, Abbica"}
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
    r = s.find_swimmer_history_by_lname('biancaniello, abbica')
    print json.dumps(r[0])
    if r is not None:
        print "    Found %s times!"%len(r)
    for a in r:
        print "    %s:%s"%(a['startdate'],a['eventname'])

