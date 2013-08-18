'''
Created on May 29, 2013

@author: jdrumgoole
'''
import threading
import Queue
from basetools import debug
import os

class FileUpdate( threading.Thread ):
    
    def __init__(self, filesCollection, checksumCalculator ):
        threading.Thread.__init__(self, name="File Updater")
        self._updateQueue   = Queue.Queue()
        self._filesCollection = filesCollection
        self._checksumCalculator = checksumCalculator
        self._runEvent = threading.Event()
        self._updateCount = 0
        
    def updateQueue(self):
        return self._updateQueue
    
    def queueFile(self, path ):
        self._updateQueue.put( path )
         
    def addFile(self, p ):
        if not os.path.islink( p ) :
            return self._filesCollection.addFile( p )
        else:
            debug.debug( "%s : is a symlink" % p )
            return None
                
     

    def queueSize(self):
        return self._updateQueue.qsize()
    
    def updateCount(self):
        return self._updateCount
        
    def stop(self):
        self._runEvent.clear()
        
    def run(self):
        self._runEvent.set()
        while self._runEvent.is_set() or ( self._updateQueue.qsize() > 0 ) :
            p = self._updateQueue.get()
            self.addFile(p)
            self._updateQueue.task_done()
            
        
