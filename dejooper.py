#!/usr/local/bin/python2.7
# encoding: utf-8
'''
filedb.dejooper -- Scan a tree of files and capture fileStat data. Use the 
filestat data to detect duplicates.

Joe.Drumgoole@10gen.com

'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

import duplicatefiledb
import pymongo

from basetools import timer, debug
from filewalker import FileWalker, FilterWalker
import time

__all__ = []
__version__ = 0.1
__date__ = '2013-08-14'
__updated__ = '2013-08-14'

DEBUG = 1
TESTRUN = 0


def findSameNames( filesCollection ):
    pass

def findDuplicates( filesCollection ):
    for ( p1, checksum ) in filesCollection.allDuplicates() :
        print "File : %s has duplicates" % p1
        for ( p2, ctime ) in filesCollection.getDuplicates( p1, checksum ):
            ltime = time.localtime( ctime )
            print "    created: %s, %s" % (time.asctime( ltime ), p2 )
            if p1 == p2 :
                print "Same file"
                sys.exit(1)
                
def scanFiles( filesCollection, d ):
    
    timing = timer.Timer()
    
    count = 0
    topDown = True
    
    walker = FilterWalker( FileWalker( topDown ), (lambda all_files:True ))
    
    timing.start()
    for f in walker.walk( d ):
        count = count + 1
        debug.msg( "Checking: %s" % f )
        filesCollection.addFile( os.path.realpath( f ))
    timing.stop()
    
    return ( count, timing.elapsed())


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None):
    '''Command line options.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Joe.Drumgoole@10gen.com on %s.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        
        parser.add_argument( "-s", "--scan", 
                             dest="scandir", 
                             help="scan a directory for content")
        parser.add_argument( "-u", "--dedupe", 
                             dest="dedupe", action="store_true", 
                             help="produce a list of duplicate files")
        parser.add_argument( "-d", "--drop", 
                             dest="flush", action="store_true", 
                             help="drop th existing databases before scanning")
        
        # Process arguments
        args = parser.parse_args()
        
        scandir = args.scandir
        dedupe = args.dedupe
        flush = args.flush
        
        try :
            m = duplicatefiledb.DuplicateFileDB()
        except ( pymongo.errors.ConnectionFailure ) as e :
            print "%s : Is the mongo deaemon running?" %e
            exit(1)
        
        files = duplicatefiledb.FilesCollection( m.db())
        
        if args.flush :
            files.drop()
        if scandir :
            scanFiles( files, args.scandir )
            
        if dedupe:
            findDuplicates( files )

        
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
        
    sys.exit(main())
