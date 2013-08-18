'''
Created on Jul 1, 2013

@author: jdrumgoole
'''
import pymongo
from duplicatefiledb import DuplicateFileDB, FilesCollection
from filetools.checksum import Checksum
import sys
import time

def compare( path1, path2 ):
    
    if path1 == path2 :
        print "Same file: %s" % path1
        sys.exit(1)
        
    chk = Checksum()
    c1 = chk.blockComputeFile( path1 )
    c2 = chk.blockComputeFile( path1 )
    if c1 != c2 :
        print "%s is not a clone of %s" % ( path1, path2 )
        sys.exit( 1 )
        
        
if __name__ == '__main__':

    files = FilesCollection()
    
    for ( p1, checksum ) in files.allDuplicates() :
        print "File : %s has duplicates" % p1
        for ( p2, ctime ) in files.getDuplicates( p1, checksum ):
            ltime = time.localtime( ctime )
            print "    created: %s, %s" % (time.asctime( ltime ), p2 )
            compare( p1, p2 )
        
