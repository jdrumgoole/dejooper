'''
Created on 17 Nov 2010

@author: jdrumgoole
'''
import sys
import datetime

"""
debug.py provides basic low level debugging routines. If DEBUG is on all debug() messages
are displayed. If TRACE is on all trace() messages are displayed. Has no application dependencies so can be used
in very low level code.
"""

TRACE=False
DEBUG=False
VERBOSE=False
        
def message( s ):
    msg( s )

def msg( s ):
    print s
    
def statusmsg(status,  s ):
    timestamp = datetime.datetime.now().strftime( "%c")
    s = "%s: %s : %s" % ( timestamp, status, s )
    msg( s )
    
def debugmsg( s ):
    debug(s)
        
def debug( s ):
    if DEBUG:
        statusmsg( "DEBUG", s )
        
def verbose( s ):
    if VERBOSE:
        statusmsg( "VERBOSE", s )

def trace( s="", o=None ):
    if TRACE:
        f = sys._getframe(1)
        print "CALLED:",
        if ( o != None ):
            print "%s." % o.__class__.__name__,
        print "%s" % f.f_code.co_name,
        print "(line: %s)" % f.f_lineno,
        statusmsg( "TRACE", s )

def debugon():
    global DEBUG
    DEBUG=True
    return DEBUG

def debugison():
    global DEBUG
    return DEBUG

def verboseison():
    global VERBOSE 
    return VERBOSE

def verboseon():
    global VERBOSE
    VERBOSE = True
    return VERBOSE
    
def verboseoff():
    global VERBOSE
    VERBOSE = False
    statusmsg( "VERBOSE", "Verbose off" )
    
def debugoff():
    global DEBUG
    statusmsg( "DEBUG", "Debugging output is off" )
    DEBUG=False
    return DEBUG

def traceon():
    global TRACE
    statusmsg("TRACE", "Tracing on")
    TRACE=True
    return TRACE

def traceoff():
    global TRACE
    statusmsg( "TRACE", "Tracing off")
    TRACE=False
    return TRACE

if __name__ == "__main__":
    debugon()
    debug( "Debug is on and the message should be displayed" )
    debugoff()
    debug( "This debug message should not be displayed" )
    traceon()
    trace("Tracing is on here")
    traceoff()
    trace("Tracing is off here")
    debugon()
    debug( "Tracing is off here")
