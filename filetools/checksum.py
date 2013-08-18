'''
Created on Mar 3, 2009

@author: jdrumgoole
'''

import hashlib
import os
import threading
import time
import unittest
import Queue

from testtools import randomutils
from basetools import timer 
from basetools import debug

class Checksum :
        
    def __init__( self, blockSize = 1024 * 100, delay = 0 ):
        # Block size limits the amount of data that is read before updating the checksum
        # Delay allows the caller to yield to other threads by inserting a finite delay between each block
        # read event.
        

        self._blockSize = blockSize
        self._zeroHash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self._delay = 0
        
    def zeroHash(self):
        return self._zeroHash

    
    def sha256Data(self, s ):
        h = hashlib.sha256()
        h.update( s )
        return h.hexdigest()
    
        
    def sha256(self, filename ):
        return self.blockComputeFile( filename )
    
    def blockComputeFile( self, filename ):
        
        digest = ""
        
        if os.path.exists( filename ):
            size = os.path.getsize( filename )

            if size == 0 :
                digest = self._zeroHash
            else:
                h = hashlib.sha256()
                remainder = size % self._blockSize
                count = size / self._blockSize
                
                if remainder > 0 :
                    count = count + 1
                try:
                    with open( filename, "rb" ) as  f:
                    
                        for _ in xrange( count ) :
                            h.update( f.read( self._blockSize ))
                            if self._delay > 0 :
                                time.sleep( self._delay )
                                
                    digest = h.hexdigest()
                    
                except ( IOError, EOFError, OSError, SystemError) as e :
                    debug.debug( "BlockComputeFile exception: %s" % e )
                    digest = None
                    
        return digest
            
    
    def compute( self, filename ):
        h = hashlib.sha256()
        with open( filename, "rb") as f:
            h.update( f.read() )
        return h.hexdigest()

class ThreadedChecksum( threading.Thread ):
    
    def __init__(self, filesCollection, blocksize = 1024 * 100 ):
            threading.Thread.__init__(self, name="Checksum Calculator")
            self._pathQueue = Queue.Queue()
            self._checksum = Checksum( blocksize )
            self._result = -1
            self._running = False
            self._filesCollection = filesCollection
            self._runEvent = threading.Event()
    
    def addFile(self, p ):
        
        sha256 = ""
        timing = timer.Timer()
        try:
            debug.debug( "%s : %i" % ( p, os.path.getsize( p )))
            timing.start()
            sha256 = self._checksum.blockComputeFile( p )
            timing.stop()
            debug.debug( "sha256 : %s" % ( sha256 ))
        except ( IOError, EOFError, OSError, SystemError) as error:
            sha256 = "" #if the file goes away ignore that
            print "exception thrown in checksum calculation: %s for %s" % ( error, p )
            
        self._filesCollection.updateChecksum( p, sha256, timing.elapsed())
            

    def queueFile(self, path ):
        self._pathQueue.put( path )
        
    def stop(self):
        self._runEvent.clear()

    def queueSize(self):
        return self._pathQueue.qsize()
    
    def run(self):
        self._runEvent.set()
        while self._runEvent.is_set() or self._pathQueue.qsize() > 0 :
            p = self._pathQueue.get()
            self.addFile( p )
            self._pathQueue.task_done()
            
            
class testChecksum( unittest.TestCase ):
    
    def testBlock( self ):
        
        f = randomutils.RandomFileHere( size = 0)
        c = Checksum()
        self.assertEqual( c.blockComputeFile( f.name()), c.compute( f.name()))
        f.rm()
        
        f = randomutils.RandomFileHere( size = 1024 )
        c = Checksum()
        self.assertEqual( c.blockComputeFile( f.name()), c.compute( f.name()))
        f.rm()
        
        f = randomutils.RandomFileHere( size = 2048 )
        c = Checksum()
        self.assertEqual( c.blockComputeFile( f.name()), c.compute( f.name()))
        f.rm()
        
        f = randomutils.RandomFileHere( size = 2048 )
        c = Checksum( blockSize = 33 )
        self.assertEqual( c.blockComputeFile( f.name()), c.compute( f.name()))
        f.rm()
 
        f = randomutils.RandomFileHere( size = 2048 * 13 )
        c = Checksum( blockSize = 333 )
        self.assertEqual( c.blockComputeFile( f.name()), c.compute( f.name()))
        f.rm()
        
        
if __name__ == "__main__" :
    unittest.main()
        