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

from filescollection import FilesCollection

from basetools import timer, debug
from filewalker import FileWalker, FilterWalker
import time
import requests
from filetools import filestat
from filetools.checksum import Checksum
import socket
import json


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
                
def webUpload( host, checksum, path ):
    
    statInfo = filestat.FileStat( path )
    
    payload =  { "host"     : socket.gethostname(),
                 "path"     : path,
                 "filename" : os.path.basename( path ),
                 "size"     : statInfo.size(),
                 "ctime"    : statInfo.ctime(),
                 "atime"    : statInfo.atime(),
                 "mtime"    : statInfo.mtime(),
                 "isdir"    : statInfo.isdir(),
                 "checksum" : checksum }
    
    headers = {'content-type': 'application/json'}
    
    requests.post( host + "/add", 
                   data=json.dumps( payload ),
                   headers=headers )
    
def scanFiles( filesCollection, d, upload, host ):
    
    timing = timer.Timer()
    
    count = 0
    topDown = True
    
    walker = FilterWalker( FileWalker( topDown ), (lambda all_files:True ))
    
    timing.start()
    for f in walker.walk( d ):
        count = count + 1
        path = os.path.realpath( f )
        debug.msg( "Checking: %s" % path )
        checksum = filesCollection.addFile( path )
        if upload :
            webUpload( host, checksum, path  )
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
        parser.add_argument( "-p", "--putone", 
                             dest="onefile",
                             help="add a single file to the DB")
        parser.add_argument( "-w", "--webupload", 
                             dest="webupload",
                             help="upload files to web db")
        parser.add_argument( "-g", "--sizegreater", 
                             dest="sizegreater",
                             type=int,
                             help="files greater than X bytes in size")
        parser.add_argument( "-l", "--sizelesser", 
                             dest="sizelesser",
                             type=int,
                             help="files less than X bytes in size")
        parser.add_argument( "-m", "--samename", 
                             dest="samename",
                             action="store_true",
                             help="report files with the same name")
        
        # Process arguments
        args = parser.parse_args()
        
        serverHost=""
        
        if args.serverHost is None :
            serverHost = "http://localhost:8080/"
        else:
            serverHost = args.serverHost

        scandir = args.scandir
        dedupe = args.dedupe
        flush = args.flush
        onefile = args.onefile
        webUpload = args.webupload
        sizeGreater = args.sizegreater
        sizeLesser = args.sizelesser
        sameName = args.samename
        
        if sizeGreater is None :
            sizeGreater = 0 
            
        if sizeLesser is None or sizeLesser == 0 :
            sizeLesser = sys.maxint
            
        files = FilesCollection()
        
        if flush :
            files.dropDB()
        if onefile:
            files.addFile( onefile )
            sys.exit(0)
        if scandir :
            scanFiles( files, args.scandir, webUpload, serverHost )
            
        if args.sizegreater or args.sizelesser :
            print "size: g:%i l:%i" % (sizeGreater, sizeLesser )
            for (path, size ) in files.sizes( sizeGreater, sizeLesser ):
                print "%s %i" % (path, size )
            
        if dedupe:
            findDuplicates( files )
            
        if sameName:
            for f in files.sameFilenames() :
                print f
        
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
