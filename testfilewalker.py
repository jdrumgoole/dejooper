'''
Created on Jun 2, 2013

@author: jdrumgoole
'''
import unittest
from testtools import randomutils, randomtree
import filewalker
from filescollection import FilesCollection
from basetools import debug

class TestFileWalker(unittest.TestCase):


    def setUp(self):
        self._files = FilesCollection( "fc" )
    
    def tearDown(self):
        self._files.dropDB()


    def testEmptyDir(self):
        
        d = randomutils.RandomDir()
        filewalker.processFiles( self._files, d())
        self.assertTrue( self._files.inFilesCollection(d()))
        self.assertEqual( 1, self._files.count())
        d.rmdir()

    def testOneFileDir(self):
#         debug.debugon()
#         debug.traceon()
        d = randomutils.RandomDir()
        f = randomutils.RandomFile(d())
        filewalker.processFiles( self._files, d())
        self.assertTrue( self._files.inFilesCollection( f()))
        self.assertEqual( 2, self._files.count())
        f.rm()
        d.rmdir()
        
    def testTree(self):
        root = randomutils.RandomDir()
        
        t = randomtree.RandomTree( root(), dirsPerDir=0, depth=1 )
        filewalker.processFiles( self._files, t.rootDir())

#         print "root       : %s" % root()
#         print "Tree Files : %s" % sorted( [ x for x in t.allPaths() ] )
#         print "Db Files   : %s" % sorted( [ x for x in self._files.allPaths()])
        
        self.assertEqual( t.totalCount(), self._files.count())
        t.rm()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
