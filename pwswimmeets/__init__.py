'''
pwswimmeets is a python implementation of the various APIs available to gather 
swim meet results in Prince William County, Virginia.
'''
__version__ = '0.0.1'
__author__ = 'Mike Biacaniello'
__maintainer__ = 'Mike Biacaniello'
__email__ = 'chepazzo@gmail.com'

from pwsl import SwimMeetServices
from rftw import RFTW
from utils import *

__all__ = ['pwsl','rftw','utils']
