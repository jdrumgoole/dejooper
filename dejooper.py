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
        print "File : %s has duplicates" % ( p1 )
        for ( host, p2, ctime ) in filesCollection.getDuplicates( p1, checksum ):
            ltime = time.localtime( ctime )
            print "    %s %s://%s" % ( time.asctime( ltime ), host, p2 )
            if p1 == p2 :
                print "Same file"
                sys.exit(1)
                
def uploadFile( host, checksum, path ):
    
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
        try :
            count = count + 1
            path = os.path.realpath( f )
            debug.msg( "Checking: %s" % path )
            checksum = filesCollection.addFile( path )
            if upload :
                uploadFile( host, checksum, path  )
        except OSError :
            continue
    timing.stop()
    
    return ( count, timing.elapsed())


def main(argv=None):
    '''Command line options.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    try:
        # Setup argument parser
        parser = ArgumentParser(description="dejooper 0.1beta", formatter_class=RawDescriptionHelpFormatter)
        
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
                             action="store_true",
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
        parser.add_argument( "-x", "--host", 
                             dest="serverHost",
                             help="host to upload to")
        parser.add_argument( "-n", "--dbname", 
                             dest="dbname",
                             default="filemetadata",
                             help="which database do we want to use")
        
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
        oneFile = args.onefile
        webUpload = args.webupload
        sizeGreater = args.sizegreater
        sizeLesser = args.sizelesser
        sameName = args.samename
        dbName = args.dbname 
        
        if sizeGreater is None :
            sizeGreater = 0 
            
        if sizeLesser is None or sizeLesser == 0 :
            sizeLesser = sys.maxint
            
        files = FilesCollection( dbname = dbName )
        
        if flush :
            files.dropDB()
            
        if oneFile:
            checksum = files.addFile( oneFile )
            if webUpload :
                uploadFile( serverHost, checksum, os.path.abspath( oneFile ))
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

if __name__ == "__main__":
        
    sys.exit(main())
