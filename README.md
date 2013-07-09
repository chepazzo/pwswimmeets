pwswimmeets
===========

API to pwswimmeets data

This is meant to be a progromattic API to get at the Swim Meet data for Prince William County VA.

See http://www.pwswimmeets.com/swimmeetservices.asmx for full cmd reference.

See http://www.pwcweb.com/makos/PWSL_2003_Time_Standards.htm for PWA and PWB times.

Examples
--------
(swimmers' names have been replaced with fake names)

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

