'''
pwswimmeets is a python implementation of the various APIs available to gather 
swim meet results in Prince William County, Virginia.

This package simplifies the collection of data from reachthewall.com and pwswimmeets.com.

See http://www.pwswimmeets.com/swimmeetservices.asmx for full pwsm cmd reference.

cmd ref for reachthewall.com has been pieced together with the help of FireBug while browsing the site.
'''


__version__ = '0.0.3'
__author__ = 'Mike Biacaniello'
__maintainer__ = 'Mike Biacaniello'
__email__ = 'chepazzo@gmail.com'
__url__ = 'https://github.com/chepazzo/pwswimmeets'
__shortdesc__ = 'API for swimmer data for Prince William County, Virginia.'

import pwsl
import rftw
import utils
import logging
import settings
from swimming import Swimmer

import re
from dateutil import parser as parsedate

__all__ = ['pwsl','rftw','utils','settings']

log = logging.getLogger(__name__)

if __name__ == '__main__':
    settings.DATAFILES['TIMESTANDARDS'] = './data/timestandards.json'
    settings.DATAFILES['EVENTS'] = './data/timestandards.json'
    settings.DATAFILES['SWIMMERS'] = './data/timestandards.json'
    log.setLevel(logging.DEBUG)
    import json
    stand = json.load(open(settings.DATAFILES['TIMESTANDARDS'],'rb'))
    s = stand[0]
    print "%s %sm %s PWB:%s PWA:%s"%(s['Event'],s['Dist'],s['Stroke'],s['PWB'],s['PWA'])

