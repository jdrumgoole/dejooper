'''
Created on 20 Nov 2010

@author: jdrumgoole
'''
import os
import stat
import logging
from itertools import izip

from enum import Enum

from filetools.checksum import Checksum

from basetools.feedback import SimpleFeedback

def normalisePath( p ):
    return os.path.normpath( os.path.normcase( p ))

def splitPath( p ):
    
    pathElements = []
    ( tail, head ) = os.path.split( normalisePath( p ))
    
    while len( head) > 0 :
        pathElements.append( head )
        ( tail, head ) = os.path.split( tail )
        
    pathElements.reverse()
    
    return pathElements
        

class DirUtils( object ):
    
    def __init__( self, d ):
        '''
        Make a DirUtil object that provides utility functions over a single directory
        d = directory name (a string)
        '''
        
        self._d = d
        self._files = os.listdir( self._d )
        self._current = 0
        
    def __iter__(self):
        return self
    
    def refresh(self):
        self._files = os.listdir( self._d )
        
    def next(self):
        if self._current == len( self._files ) :
            self._current = 0
            raise StopIteration
        else:
            rv = self._files[ self._current ]
            self._current += 1
            return rv
        
    def dirname(self):
        '''
        return the dirname
        '''
        return self._d
    
    def __len__(self):
        '''
        Size of a directory in terms of no of files
        '''
        return len( self._files )
    
    def fileList(self, sortedList = False):
        '''
        Return a list of all the file (i.e. no dir) objects in a directory
        Don't sort return value unless sorted is true.
        '''
        result = []
        for i in self.listAll( sortedList = sortedList ):
            if os.path.isfile( i ):
                result.append( i )
                
        return result
            
    def dirList(self, sortedList = False):
        result = []
        for i in self.listAll( sortedList = sortedList ):
            if os.path.isdir( i ):
                result.append( i )
                
        return result   
        
    def size(self):
        s=0
        for f in self.fileList() :
            s = s + os.path.getsize( f )
                
        return s
    
    def fileCount(self):
        return len( self.fileList())
    
    def dirCount(self):
        return len( self.dirList())
    
    def listAll(self, fullPath=True, sortedList = False ):
        result = []
        for i in os.listdir( self._d) :
            if fullPath :
                path = os.path.abspath( os.path.join( self._d, i ))
            else:
                path = i
            result.append( path )
            
        if sortedList :
            result.sort()
            
        return result
        
    
class FileCompare( object ):
    
    def __init__(self, f1, f2 ):
        self._f1 = normalisePath( f1 )
        self._f2 = normalisePath( f2 )
        
    def pathCompare( self ):
        return self._f1 == self._f2
    
    def reverseCompare(self):
        p1 = splitPath( self._f1 )
        p2 = splitPath( self._f2 )
    
        p1.reverse()
        p2.reverse()
        
        matchCount = 0
        for i, j in izip( p1, p2 ):
            if i == j :
                matchCount = matchCount + 1
            else:
                break
        
        p1.reverse() # put list back in order for return
        if matchCount > 0 :  
            return p1[-matchCount:]
        else:
            return []
            
    def forwardCompare(self):
        '''
        Compare two target files from root down. Return number of path
        elements that are identical.
        '''
        
        p1 = splitPath( self._f1 ) 
        p2 = splitPath( self._f2 )
        
        matchCount = 0
        for i, j in izip( p1, p2 ):
            if i == j :
                matchCount = matchCount + 1
            else:
                break

        if matchCount > 0 :  
            return p1[:matchCount]
        else:
            return []
        
    def sizeCompare(self):
        
        return os.path.getsize( self._f1 ) == os.path.getsize( self._f2 )
    
    def checksumCompare(self):
        return Checksum().blockComputeFile( self._f1 ) == Checksum().blockComputeFile(self._f2 )
    
    def binCompare(self):
        if self.pathCompare() : # identical files
            return True
        elif self.sizeCompare() and self.checksumCompare():
            return True
        else:
            return False

class DiffSet:
    
    def __init__(self, rhs, lhs):
        self._smallest = min( rhs, lhs )
        self._lhsSet = frozenset( lhs )
        self._rhsSet = frozenset( rhs )
        self._isEqual = ( self._lhsSet == self._rhsSet )
        self._lhsDiff = self._lhsSet.difference( self._rhsSet )
        self._rhsDiff = self._rhsSet.difference( self._lhsSet ) 
    
    def lhsDiff(self):
        return self._lhsDiff
    
    def rhsDiff(self):
        return self._rhsDiff
        
    def __len__(self):
        return len( self._lhsSet ) + len( self._rhsSet )
    
class DirCompare( object ) :
    '''
    Compare to directorys. Dirs are parsed during object creation
    '''
    
    def __init__(self, d1, d2 ) :
        
        self._d1 = DirUtils( d1 )
        self._d2 = DirUtils( d2 )
        self._d1List = self._d1.listAll(fullPath=False)
        self._d2List = self._d2.listAll(fullPath=False)
        self._d1List.sort()
        self._d2List.sort()
 
    def lengthCompare(self):
        return len( self._d1 ) == len( self._d2 )
    
    def filesCompare(self):
        pass
            
    def dirsCompare(self):
        pass
    
    def sizeCompare(self):
        
        return self._d1.size() == self._d2.size()
                
    def nameCompare(self):
        '''
        Compare two directories and return a list of files that match within the directory.
        For two identical directories the len(d1) = len(d2) = len( foundList) and
        sort( os.listDir( d1 ) = sort( os.listdir( d2)) = sort( foundList )
        '''
        
        ds = DiffSet( self._d1, self._d2 )
        
        return ds
        

class LogCmd :
    
    def __init__(self, logFilename, commentChar = "#" ):
        
        self._log = logging.getLogger( "LOGCMD" )
        self._log.setLevel( logging.INFO )
        self._LogFilename = logFilename
        self._commentChar = commentChar
        self._handler = logging.handlers.RotatingFileHandler(self._logFilename,
                                                             maxBytes =  10000,
                                                             backupCount = 3 )
        
        formatString = "%s %s : %s" % ("%(asctime)s", "%(name)s", "%(message)s",   )
        self._formatter = logging.Formatter( formatString )
        self._handler.setFormatter( self._formatter )
        self._log.addHandler( self._handler )
        
        
    def name(self):
        return self._logFilename
    
    def logCmd(self, s ):
        self._log.info( s )
        
    def logComment( self, c ):
        comment = "%s %s" % ( self._commentChar, c )
        self._log.info( comment )

class FileAttrs :
    
    DIR      ="dir"
    CHAR     ="char"
    FIFO     ="fifo"
    REGULAR  ="regular"
    BLOCK    = "block"
    LINK     = "link"
    SOCKET   = "socket"

    fileType = ( DIR, CHAR, FIFO, REGULAR, BLOCK, LINK, SOCKET )

    
    def __init__( self, name=None, size=0, computeChecksum=True ) :
        
        self._fileType = Enum( "dir",
                               "char", 
                               "fifo", 
                               "regular",
                               "block",
                               "link",
                               "socket" )
        
        self._name = name
        self._size = size
        self._creationDate = None
        self._modificationDate = None
        self._accessDate = None
        self._checksum = None
        self._type = None
        
        if name :
            st = os.stat( name )
            
            if stat.S_ISDIR( st[ stat.ST_MODE ]):
                self._type = self._fileType.dir
            elif stat.S_ISREG(st[ stat.ST_MODE ]):
                self._type = self._fileType.regular
                self._size = st[ stat.ST_SIZE ]
                if computeChecksum :
                    self._checksum =  Checksum().sha256( name )
            elif stat.S_ISLNK( st[ stat.ST_MODE ]):
                self._type = self._fileType.link
            elif stat.S_ISBLK( st[ stat.ST_MODE ]):
                self._type = self._fileType.block
            elif stat.S_ISSOCK( st[ stat.ST_MODE ]):
                self._type = self._fileType.sock
            elif stat.S_ISCHR( st[ stat.ST_MODE ]) :
                self._type = self._fileType.char
            elif stat.S_ISFIFO( st[ stat.ST_MODE ]) :
                self._type = self._fileType.char
                
            self._creationDate     = st[ stat.ST_CTIME ]
            self._modificationDate = st[ stat.ST_MTIME ]
            self._accessDate       = st[ stat.ST_ATIME ]
            
            #Sha256 from zero length file computed from http://www.xorbin.com/tools/sha256-hash-calculator
            self._zeroHash         = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    def fileType(self):
        return self._type
    
    def creationDate(self):
        return self._creationDate
    
    def modificationDate(self):
        return self._modificationDate
    
    def accessDate(self ):
        return self._accessDate
    
    def size( self ):
        return self._size

    def isDir(self):
        return self._type == self._fileType.dir

    def isFile(self):
        return self._type == self._fileType.regular 
    
    def dirname(self):
        return os.path.dirname( self._name )
    
    def basename(self):
        return os.path.basename( self._name )
    
    def name(self ):
        return self._name 

    def setSize(self, size ):
        self._size = size
        
    def setName(self, name ):
        self._f = name 
        
    def setChecksum(self, sum ):
        self._checksum = sum
        
    def checksum(self):
        if self._checksum == None :
            raise ValueError( "Checksum not set for %s" % self._name )
        return self._checksum
        
class FileOps :
    
    def __init__(self, bufferSize = 10000, 
                 logCmd=None, flush = None,
                 feedback = SimpleFeedback() ):
        
        self._bufSize = bufferSize
        self._log = logCmd
        self._flush = flush
        self._feedback = feedback
        
    def isEqual(self, f1, f2 ):
        
        a1 = FileAttrs( f1 )
        a2 = FileAttrs( f2 )
        
        if a1.isDir() and a2.isDir() :
            return a1.basename() == a2.basename()
        
        if  a1.isFile() and a2.isFile() :
            return (( a1.basename() == a2.basename()) and
                    self.checksumIsEqual(f1, f2))
        else :
            return False
    
    def copyblock(self, src, sink, xfer  ):
        b = src.read( self._bufSize )
        sink.write( b )
        if self._flush:
            sink.flush()
            
        return xfer + len( b )
      
    def copyfile( self, f1, f2 ):
        
        xfer = 0  

        srcAttrs = FileAttrs( f1 )
        with open( f1, "rb" ) as src:
            with open( f2, "wb" ) as sink:

                blocks = srcAttrs.size() / self._bufSize
                remnant= srcAttrs.size() % self._bufSize
                
                if remnant > 0 :
                    blocks = blocks + 1 
                for i in xrange( blocks ):
                    xfer = self.copyblock( src, sink, xfer )
                    if self._feedback :
                        self._feedback.progress( f2, srcAttrs.size(), xfer )
                    
        if self._log:
            self._log.logcopy( srcAttrs, FileAttrs( f2 ))
            
    def makedir(self, d  ):
        #print "makedir: '%s'" % d
        os.makedirs( d )
        if self._log:
            self._log.logmkdir( d )
        
    def checksumIsEqual(self, f1, f2 ):
        
        chk = Checksum()
        
        if os.path.isfile( f1 ) and os.path.isfile( f2 ) :
            return (( os.path.getsize( f1 ) == os.path.getsize( f2 )) and
                    ( chk.sha256( f2 ) == chk.sha256( f2 )))
        else:
            return False
  
    