'''
Created on 17 Nov 2010

@author: jdrumgoole
'''

import time
import math

def intRemainder( s, factor, rounding = 0  ):
    return (s /factor,s % factor )

def floatRemainder( s, factor, rounding = 0  ):
    f = s /factor
    ( remainder, divisor ) = math.modf( f )
    remainder = remainder * factor
    return ( divisor, remainder )

class PeriodsInSeconds:
    milli      = 0.001
    hundreth   = 0.01
    tenth      = 0.1
    second     = 1
    minute     = 60 * second
    hour       = 60 * minute
    day        = 24 * hour
    week       = 7 * day
    month      = 4 * week
    year       = 12 * month
    
def secondsToPeriod( s ):
    
    remainder = s
    ( years, remainder )     = intRemainder( remainder, PeriodsInSeconds.year )
    ( months, remainder )    = intRemainder( remainder, PeriodsInSeconds.month )
    ( weeks, remainder )     = intRemainder( remainder, PeriodsInSeconds.week )
    ( days, remainder )      = intRemainder( remainder, PeriodsInSeconds.day )    
    ( hours, remainder )     = intRemainder( remainder, PeriodsInSeconds.hour )
    ( minutes, remainder )   = intRemainder( remainder, PeriodsInSeconds.minute )
    ( seconds, remainder )   = intRemainder( remainder, PeriodsInSeconds.second )
    
    ( tenths, remainder )    = floatRemainder( remainder, PeriodsInSeconds.tenth )
    ( hundreths, remainder ) = floatRemainder( remainder, PeriodsInSeconds.hundreth  )  
    ( millis, remainder )    = floatRemainder( remainder, PeriodsInSeconds.milli )
    
    return ( round(years), 
             round(months), 
             round(weeks), 
             round(days), 
             round(hours), 
             round(minutes), 
             round(seconds), 
             round(tenths), 
             round(hundreths), 
             round(millis ))

def MinsSecsHundreths( elapsedSeconds ):
    
    ( yrs, mths, wks, days, hours, mins, secs, tenths, hdths, millis ) = secondsToPeriod( elapsedSeconds )
    
    return ( mins, secs, ( tenths * 10 + ( hdths )))

def timeFormat( hours, mins, hundredths ):
    return "%s:%s.%s" % ( int( hours ), int( mins ), int( hundredths ))
    
class Timer(object):
    #
    # A timer object counts elapsed time between  a start event and a stop event.  The timer can be initialised
    # with a time from which counting starts.
    #
    
    def __init__(self, startNow=False, initialTime=0):
        self._initialTime= initialTime
        self._start = 0
        self._stop = 0
        self._timerOn = False
        if startNow:
            self.start( initialTime = self._initialTime )

    def start(self, initialTime = 0 ):
        self._timerOn = True
        self._initialTime = initialTime
        self._start = time.time()
        return self._start

    def stop(self):
        if self._timerOn :
            self._stop = time.time()
            self._timerOn = False
        return self._stop - self._start + self._initialTime

    def is_timing(self):
        return self._timerOn

    def elapsed(self):
        if (self._timerOn):
            seconds = time.time() - self._start + self._initialTime
        else:
            seconds = self._stop - self._start + self._initialTime
        return seconds

    def __repr__(self):
        ( mins, secs, hundreths ) = MinsSecsHundreths( self.elapsed())
        return timeFormat( mins, secs, hundreths )
    
    def __str__(self):
        return self.__repr__()
    
    