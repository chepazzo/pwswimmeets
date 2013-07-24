pwswimmeets
===========

API to pwswimmeets data

This is meant to be a progromattic API to get at the Swim Meet data for Prince William County VA.

See http://www.pwswimmeets.com/swimmeetservices.asmx for full cmd reference.

See http://www.pwcweb.com/makos/PWSL_2003_Time_Standards.htm for PWA and PWB times.

Modules
-------

rftw/pwsl
~~~~~~~~~

These modules present a direct interface to the two APIs.  Methods and arguments are meant to match as closely as possible the same names and formats as what the API expects.  This makes it easier to provide at least a raw implementation of the APIs even for features which haven't been convenientized yet.

swimming
~~~~~~~~

The swimming module holds all of the classes to hold the data.  Each class also has a .json property that can be used to generate a JSON serializable dict representation of the instance to use when storing to disk.

utils
~~~~~

I have also included some utility functions to help automate some tasks.

find_* tasks are meant to do a search and return a list.
gen_* tasks are meant to read data from the API and reformat/structure to be stored in a local file.
load_* tasks are meant to load the data from stored files.

Examples
--------
(swimmers' names have been replaced with fake names)


Direct API
~~~~~~~~~~
    >>> import pwswimmeets
    >>> s = pwswimmeets.SwimMeetServices()
    >>> s.find_swimmer_by_lname('phel')
    [{'DOB': None, 'HistoryResults': None, 'Age': None, 'AthName': 'Phelps, Michael', 'TeamNo': None, 'Sex': 'F', 'AthNo': '1234', 'AthTeamAbbr': 'BRB', 'Events': None}]
    >>> 
    >>> s.get_athlete('1234')
    {'DOB': '1/1/2007', 'HistoryResults': [{'ResultType': 'Back', 'History': [{'MeetDate': '07-14-2012(DCST)', 'FinTime': '1', 'DisplayTime': '1'}]}, {'ResultType': 'Breast', 'History': [{'MeetDate': '07-14-2012(DCST)', 'FinTime': '1', 'DisplayTime': '1'}]}, {'ResultType': 'Fly', 'History': [{'MeetDate': '07-14-2012(DCST)', 'FinTime': '1', 'DisplayTime': '1'}]}, {'ResultType': 'Free', 'History': [{'MeetDate': '07-14-2012(DCST)', 'FinTime': '92.93', 'DisplayTime': '1:32.93'}]}, {'ResultType': 'IM', 'History': [{'MeetDate': '07-14-2012(DCST)', 'FinTime': '1', 'DisplayTime': '1'}]}], 'Age': '99', 'AthName': 'Phelps, Michael', 'TeamNo': '9999', 'Sex': 'F', 'AthNo': '7826', 'AthTeamAbbr': 'VOSD', 'Events': ''}
    >>> 
    >>> s.get_ind_event(eventno=50,meetdb='SwimMeetVOSD')
    {'EventAthletes': [{'Status': ' ', 'AthleteName': 'Phelps, M', 'TeamAbbr': 'LR', 'dqDesc': '', 'AthNo': '228', 'Points': '13', 'Place': '1', 'Time': '19.12', 'Record': '', 'Improve': '1'}], 'EventRecords': 'False', 'EventNumber': 'Event 50', 'EventName': ' Boys 9-10 25 Meter Fly ', 'EventStatus': 'S', 'EventOrder': '52'}

Utils
~~~~~

    >>> import pwswimmeets
    >>> for season in range(2009,2013+1):
    >>>     meet_data = pwswimmeets.utils.gen_meet_results(team_abbrev='VOS',season=season)
    >>> 
    >>> vosdswimmers = [ s for s in pwswimmeets.swimming.SWIMMERS if s.team.name == 'Virginia Oaks Sea Devils' ]
    >>> 
    >>> pwswimmeets.swimming.TEAMS[21].json
    {'abbrevs': [{'source': 'rftw', 'abbrev': u'VOS'}], 'type': 'summer', 'league_name': 'Prince William Swim League', 'name': u'Virginia Oaks Sea Devils', 'ids': [{'source': 'rftw', 'id': u'189'}]}
    >>> 
    >>> vosdswimmers[0].json
    {'name': u'Phelps, Michael', 'strokes': [{'stroke': u'25 Free', 'history': [{'status': 'OK', 'PWT': 'B', 'seedtime': 20.65, 'event_name': u'Boys 8 & Under 25 Meter Free', 'season': 2009, 'meet_date': 'July 25, 2009', 'meet_id': u'816', 'points': u'15.000', 'place': u'4', 'time': 21.84, 'event_num': u'10'}]}], 'sex': u'M', 'swimmer_ids': [{'source': 'rftw', 'id': u'Phelps,Michael258965000'}], 'dob': None, 'team': u'Virginia Oaks Sea Devils'}
    >>> 


