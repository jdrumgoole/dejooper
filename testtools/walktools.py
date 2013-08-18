'''
Created on Aug 11, 2013

@author: jdrumgoole
'''

import os
import unittest
from randomtree import RandomTree

class Walker :

    def __init__(self, topDown = True  ):
        self._topDown = topDown
        
        
    def walk( self, top ):
        for ( path, dirnames, files ) in os.walk( top, self._topDown ) :
            yield path
            for f in files:
                yield os.path.join( path, f )
        
    def count(self, path ):
        
        dirCount = 0
        fileCount = 0
        
        for ( path, _, files ) in os.walk( path, self._topDown ) :
            dirCount = dirCount + 1
            for f in files :
                fileCount = fileCount + 1 
                
        return ( dirCount, fileCount )
    
    def dirs(self, path ):
        
        for ( path, _, _ ) in os.walk( path, self._topDown ):
            yield path
            
    def files(self, path ):
        
        for ( _, _, files ) in os.walk( path, self._topDown ):
            for f in files :
                yield f
                
class TestFileWalker(unittest.TestCase):


         
    def setUp(self):
        self._w = Walker() 
        
        
    def depthFunction(self, depth, dirsPerDir, filesPerDir ):
        
        d = RandomTree( depth=depth, 
                        dirsPerDir=dirsPerDir, 
                        filesPerDir=filesPerDir  )
        dirsCalc = d.dirsCalculation(depth, dirsPerDir)
        self.assertEqual( dirsCalc, d.dirsCount())
        self.assertEqual( dirsCalc * filesPerDir, d.filesCount())
        d.rm()
        
    def testDirCount(self):
        
        d = RandomTree()
        
        dc = d.dirsCalculation(depth=1, dirsPerDir=0 )
        
        #print "dirs x: %s" % d.dirs()
        
        self.assertEqual( 1, dc )
        
        dc = d.dirsCalculation(depth=1, dirsPerDir=1 )
        
        self.assertEqual( 2, dc )
        
        d.rm()

    def testWalkCounts(self):
        
        for depth in range( 4 ) :
            for dirsPerDir in range( 4 ) :
                for filesPerDir in range( 4 ) :
                    #print "depth: %i, dpd : %i, fc: %i" % (depth, dirsPerDir, filesPerDir )
                    self.depthFunction(depth, dirsPerDir, filesPerDir) 
                    
#         d = RandomTree( depth = 1, dirsPerDir = 0, filesPerDir = 0 )
#         
#         self.assertEqual( 1, d.dirsCount())
#         self.assertEqual( 0, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 1, dirsPerDir = 1, filesPerDir = 0 )
#         
# 
# 
#         self.assertEqual( 2, d.dirsCount())
#         self.assertEqual( 0, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 1, dirsPerDir = 1, filesPerDir = 1 )
#         
#         self.assertEqual( 2, d.dirsCount())
#         self.assertEqual( 2, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 1, dirsPerDir = 2, filesPerDir = 2 )
#         
# #         print "Root  : %s" % d.rootDir()
# #         print "dirs  : %s" % d.dirs()
# #         print "files : %s" % d.files()
#         
#         self.assertEqual( 3, d.dirsCount())
#         self.assertEqual( 6, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 1, dirsPerDir = 3, filesPerDir = 2 )
#         
#         self.assertEqual( 4, d.dirsCount())
#         self.assertEqual( 8, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 2, dirsPerDir = 1, filesPerDir = 1 )
#         
#         # root 
#         #    f1
#         #    d1
#         #      f2
#         #      d2
#         #        f3
#         self.assertEqual( 3, d.dirsCount())
#         self.assertEqual( 3, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 2, dirsPerDir = 3, filesPerDir = 2 )
#         #
#         # root
#         #    d1
#         #       dl1
#         #       dl2
#         #       dl3
#         #    d2
#         #       dl1
#         #       dl2
#         #       dl3
#         #    d3
#         #       dl1
#         #       dl2
#         #       dl3
#         # 1 + dpd + dpd * depth
#         #
#         self.assertEqual( ( 1+3+3**2), d.dirsCount())
#         self.assertEqual( ( 1+3+3**2) * 2 , d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 2, dirsPerDir = 2, filesPerDir = 3 )
#         # d1 
#         #    f1
#         #    d2
#         #      f2
#         #      d2
#         #        f3
#         self.assertEqual( ( 1 + 2 + 2**2), d.dirsCount())
#         self.assertEqual((1 + 2 + 2**2)*3, d.filesCount())
#         d.rm()
#         
#         d = RandomTree( depth = 3, dirsPerDir = 4, filesPerDir = 3 )
#         self.assertEqual( ( 1 + 4**1 + 4**2 + 4**3), d.dirsCount())
#         self.assertEqual((1 + 4**1 + 4**2 + 4**3)*3, d.filesCount())
#         d.rm()
        
    def testWalk(self):
        d = RandomTree( depth = 2, dirsPerDir = 2, filesPerDir = 4 )  
        
        root =d.rootDir()
        
        ( dirCount, fileCount) = self._w.count( root )
        
        self.assertEqual( dirCount, d.dirsCount())
        self.assertEqual( fileCount, d.filesCount())
        
        self.assertEqual( sorted( [ x for x in d.dirs() ] ), sorted( d.dirs()))
        self.assertEqual( sorted( [ x for x in d.files() ]), sorted( d.files()))
        
        d.rm()
        
              
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
                