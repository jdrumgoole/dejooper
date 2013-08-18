'''
Created on Mar 3, 2009

@author: jdrumgoole
'''

import os
from optparse import OptionParser
import sys
import itertools
from dejooper.duplicatefiledb import DuplicateFileDB, FilesCollection
from basetools import debug
from basetools import timer
import pymongo

class FileWalker :
    
    def __init__( self, topDown = True ):
        self._topDown = topDown
        
    def walk( self, top ):
        for ( path, _, files ) in os.walk( top, self._topDown ) :
            yield path
            for f in files:
                yield os.path.join( path, f )
        
class FilterWalker:
    
    def __init__( self , ftw, filter_func ):
        self._ftw = ftw
        self._filter_func = filter_func
        
    def walk( self, top ):
        return itertools.ifilter( self._filter_func, self._ftw.walk( top ) )


class Counter:

    def __init__(self, top ):
        
        self._top = top
        self._ftw = FileWalker()
        self._extCount = {}
        self._fileCount = {}
        
    def count(self):
    
        root = ""
        ext = ""
        for f in self._ftw.walk( self._top ):
            print f
            ( root, ext ) = os.path.splitext( os.path.basename( f ))
            if  not self._extCount.has_key( ext ):
                self._extCount[ ext ] = 0
            if not self._fileCount.has_key( root ) :
                self._fileCount[ root ] = 0
            
            self._extCount[ ext ] = self._extCount[ ext ] + 1
            self._fileCount[ root ] = self._fileCount[ root ] + 1
            
    def __str__( self ) :
        s = "self._top = %s\n" % self._top
        for ( i, j ) in self._extCount.items():
            s = "%sExtension: \'%s\', Count: %i\n" % (s, i, j )
        for ( i, j ) in self._fileCount.items() :
            s = "%sFilename : \'%s\', Count: %i\n" % ( s, i, j )
        return s
        
    def __repr__(self):
        return "( %s, %s, %s )" % (  self._top, self._extCount, self._fileCount )

def all_files( path ):
    return True 


def processFiles( filesCollection, d ):
    
    timing = timer.Timer()
    
    count = 0
    topDown = True
    
    walker = FilterWalker( FileWalker( topDown ), all_files )
    
    timing.start()
    for f in walker.walk( d ):
        count = count + 1
        debug.msg( "Checking: %s" % f )
        filesCollection.addFile( os.path.realpath( f ))
        
    timing.stop()

    
if __name__ == "__main__":
    
    debug.debugon()
    debug.traceon()
    
    parser = OptionParser( usage = "%prog <list of files>",
                          version = "%prog release: 0.1" )
    
    parser.add_option( "-t", "--topdown", dest = "topdown",
                      help = "do a top down walk", action = "store_true", default = True )
    
    parser.add_option( "-i", "--dirsonly", dest = "dirsonly",
                      help = "filter out dirs only", action = "store_true", default = False )
    ( options, args ) = parser.parse_args()

    if options.dirsonly :
        file_filter = os.path.isdir
    else:
        file_filter = all_files
        


    if len( sys.argv ) == 1 :
        dirs = [os.getenv( 'USERPROFILE' ) or os.getenv( 'HOME' )]
    else:
        dirs = sys.argv[1:]

    try :
        m = DuplicateFileDB()
    except ( pymongo.errors.ConnectionFailure ) as e :
        print "%s : Is the mongo deaemon running?" %e
        exit(1)

    if file_filter == None:
        file_filter = all_files
        
    files = FilesCollection( m.db())
    
    for d in dirs:
        print "Processing: %s" % d
        processFiles( files, d )
        print "done"