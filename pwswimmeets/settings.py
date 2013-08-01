import os

DATAFILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')
DATAFILES = {
    'TIMESTANDARDS': DATAFILEPATH+'timestandards.json',
    'EVENTS' : DATAFILEPATH+'events.json',
    'SWIMMERS' : None,
    'TEAMS': None
}

LEAGUE = {
    'name':'Prince William Swim League',
    'id':'5',
    'abbrev':'PWSL'
}


TEAMNAME = None
