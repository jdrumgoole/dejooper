'''
Created on 29 Nov 2010

@author: jdrumgoole
'''

import unittest
import os
import string
import shutil

from testtools.randomutils import RandomString, RandomPath
from testtools.randomtree import RandomTree
from filetools.treeutils import TreeUtils

class testRandomFile( unittest.TestCase )  :
    
    def testRandomName(self):
        f = RandomPath()
        self.assertTrue( os.path.isfile( f.path()))
        f.remove()
        self.assertFalse( os.path.isfile( f.path()))
        
    def testRandomDir(self):
        
        d = RandomPath( make="DIR")
        self.assertTrue( os.path.isdir( d()))
        d.remove()
        
        d1 = RandomPath( make="DIR")
        
        d2 = RandomPath( d1(), make="DIR")
        
        self.assertTrue( os.path.isdir( os.path.join( d1(), d2())))
        
        shutil.rmtree( d1())
        
        with RandomPath( make="DIR") as d1 :
            with RandomPath( d1(), make="DIR")  as d2 :
                self.assertTrue( os.path.isdir( os.path.join( d1(), d2())))
                
        self.assertFalse(os.path.isdir( os.path.join( d1(), d2())))
        
        d1 = RandomPath( make="DIR")
        
        self.assertTrue( os.path.isdir( d1()))
        
        d1.remove()
        
        self.assertFalse( os.path.isdir( d1()))
        
    def testRandomFile(self):
        
        r = RandomPath()
        self.assertTrue( os.path.isfile( r()))
        r.remove()
        self.assertFalse(os.path.isfile(r()))
        
        r = RandomPath().populate(size = 1024)
        self.assertTrue( os.path.isfile( r()))
        self.assertEqual(os.path.getsize(r()), 1024)
        
        self.assertEqual( r(), os.path.join( r.dirname(), r.basename()))
        r.remove()
        self.assertFalse(os.path.isfile(r()))
        
        r = RandomPath()
        r.populate( 1024 )
        self.assertTrue( os.path.isfile( r()))
        self.assertEqual(os.path.getsize(r()), 1024)
        r.remove()
        self.assertFalse( os.path.isfile( r()))
        
    def testRandomFileName(self):
        f = RandomPath().populate( 1024 * 1024 )
        self.assertEqual(os.path.getsize(f()), 1024 * 1024 )
        self.assertEqual(os.path.getsize(f()), f.size())
        f.remove()
        self.assertFalse(os.path.isfile(f.path()))
        self.assertEqual( 0, f.size())
        
    def testRandomFile1024(self, size = 1024):
        r = RandomPath().populate( 1024 )
        self.assertEqual(os.path.getsize( r()), r.size())
        r.remove()
        self.assertFalse(os.path.isfile( r()))
        
    def testRandomFile2048(self):
        self.testRandomFile1024(1024 * 2)
        
    def testRandomString(self):
        
        r = RandomString( string.letters )
        
        g = r.randomChunk( 0, 0 )
        self.assertEqual( len( g.next()), 0 )
        
        g = r.randomChunk( 100, 0 )
        self.assertEqual( len( g.next()), 100 )
        
        g = r.randomChunk( -1, 0 )
        self.assertRaises( ValueError, g.next )
        #    r.randomChunk( 0, -1 )
            
        g = r.randomChunk(26, 26 )
        s = g.next()
        self.assertEqual( len( s ), 26 )
    
        g = r.randomChunk(512, 512 )
        s = g.next()
        self.assertEqual( len( s ), 512 )
        
        g = r.randomChunk( len( r.population()), len(r.population()))
        s = g.next()
        self.assertEqual( len( s ), len( r.population()))
        
        buf = ""
        c  = 0
        for i in r.randomChunk( 10500, 1000 ) :
            c = c + 1
            if c < 11:
                self.assertEqual( len( i ), 1000 )
            else:
                self.assertEqual( len( i ), 500 )
                
            buf = buf + i
            
        self.assertEqual( len( buf ), 10500 )
        
    def randomTreeHelper(self, pre, suf, size, width, depth ):
        dCount = 0
        tsize  = 0
        fCount = 0
        
        # randRoot needs to exist
        randRoot = RandomPath( prefix=pre, suffix=suf, make="DIR") ;
        t = RandomTree( randRoot(), prefix=pre, suffix=suf)
        dirCount = t.dirsCount() ;
        fileCount = t.filesCount() ;
        size = t.size() ;
        
        for i in t.dirs() :
            name = os.path.basename( i )
            self.assertTrue( os.path.isdir( i ))
            #print "name: %s" % name
            self.assertTrue( name.startswith( pre ))
            self.assertTrue( name.endswith( suf ))
            dCount = dCount + 1
            
        self.assertEqual( dirCount, dCount ) 
        
        for i in t.files() :
            name = os.path.basename( i )
            self.assertTrue( os.path.isfile( i ))
            self.assertTrue( name.startswith( pre ))
            self.assertTrue( name.endswith( suf))
            tsize = tsize + os.path.getsize( i )
            fCount = fCount + 1
            
        self.assertEqual( fileCount, fCount )
        self.assertEqual( size, tsize )
            
        td = TreeUtils()
        tData = td.data( t.rootDir())
        
        self.assertEqual(( dirCount, fileCount, size ), tData )

        t.rm()
        self.assertFalse( os.path.isdir( t.rootDir()))

    def testRandomTree(self):
        
        self.randomTreeHelper( pre="", suf="", size=0, width=1, depth=1)
        
        self.randomTreeHelper( pre="123", suf="", size=1, width=1, depth=1)
        
        self.randomTreeHelper( pre="123", suf="", size=1, width=2, depth=1)
        
        self.randomTreeHelper( pre="123", suf="XYZ", size=243, width=3, depth=2)
        
        self.randomTreeHelper( pre="123", suf="XYZ", size=243, width=3, depth=2)
        
        
if __name__ == '__main__':
    unittest.main()