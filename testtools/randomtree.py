'''
Created on 12 Jun 2009

@author: jdrumgoole
'''

from testtools.randomutils import RandomFile, RandomName, RandomDir
import os

class RandomTree :
    
    def __init__(self, location=None, size=1024, dirsPerDir=1, depth=1, filesPerDir = 1, suffix = "", prefix = ""): 
        #
        # Create a tree of randomly named files directories in directory "rootDir". The tree will have a depth
        # of "depth" and each subdirectory will have "dirsPerDir" subdirectories. Each directory will have "filesPerDir"
        # ordinary files. Each ordinary file will have a suffix defined by "suffix" and a prefix defined by "prefix".
    
        self._suffix = suffix
        self._prefix = prefix
        self._totalSize = 0
        self._files = []
        self._dirs = []
        if location == None :
            self._location = os.getcwd()
        else:
            self._location = location
            
        self._size = size
        self._dirsPerDir = dirsPerDir
        self._depth = depth
        self._filesPerDir = filesPerDir
        
        self._rootDir = RandomDir( location ).path()
        self._dirs.append( self._rootDir )
        self.make( self._rootDir, depth = self._depth )
        
    
    def makeDirs(self, rootDir ):
        
        dirs=[]
        for _ in range(self._dirsPerDir):
            thisDir = os.path.join(rootDir, RandomName().basename())
            os.mkdir( thisDir )
            dirs.append( thisDir )
            
        return dirs
    
    def makeFiles(self, rootDir ):
        
        files=[]
        
        for _ in range( self._filesPerDir ) :
            filename = RandomName( rootDir = rootDir ).basename()
            path = os.path.join(rootDir, "%s%s%s" % (self._suffix, filename, self._prefix))
        #print "makefile : %s" % path
            r = RandomFile( name = path, size= self._size)
            self._totalSize = self._totalSize + self._size
            files.append( r())
            
        return files
            
    def dirsCalculation(self, depth, dirsPerDir ):
        
        #
        # No of dirs created is a power series.
        #
        # 1 + dirsPerDir**1 + dirsPerDir**2 + .. dirsPerDir ** depth
    
        count = 1 # initial root dir
        
        for i in range( depth ) :
            count = count + dirsPerDir ** (i+1)
            
        return count
    
    def make(self, rootDir, depth = 1):
        
        # The total number of dirs created = depth * dirsPerDir + 1
        # the total number of files created = totalNoOfDirs * filesPerDir
        #
        filesList = self.makeFiles( rootDir )
        self._files.extend( filesList )
        
        if depth > 0 :
            dirList = self.makeDirs( rootDir )
            self._dirs.extend( dirList )
            for d in dirList :
                self.make( d, depth - 1)
            
    def files(self):
        return self._files
    
    def filesCount(self):
        return len( self._files )
    
    def allPaths(self):
        return self._dirs + self._files
    
    def dirs(self):
        return self._dirs
    
    def dirsCount(self):
        return len( self._dirs )
    
    def totalCount(self):
        return self.filesCount() + self.dirsCount()
    
    def size(self):
        return self._totalSize
    
    def rootDir(self):
        return self._rootDir
    
        
    def rm(self):
        
        for i in self._files :
            #print "unlink: %s" %i
            os.unlink(i)
            
        for i in reversed(self._dirs):
            #print "rmdir %s" % i
            os.rmdir(i) 
            
        self._dirs = []
        self._files = []
        self._totalSize = 0
        self._rootDir = ""
                

