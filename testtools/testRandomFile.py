'''
Created on 29 Nov 2010

@author: jdrumgoole
'''

import unittest
import os
import string
import shutil

from testtools.randomutils import RandomFile, RandomString, RandomName, RandomTree, RandomDir

from filetools.treeutils import TreeUtils

class testRandomFile( unittest.TestCase )  :
    
    def testRandomName(self):
        f = RandomName()
        self.assertFalse( os.path.isfile( f.name()))
        
        
    def testRandomDir(self):
        
        d = RandomDir()
        self.assertTrue( os.path.isdir( d.name()))
        os.rmdir( d.name())
        
        d1 = RandomDir()
        
        d2 = RandomDir( d1.name())
        
        self.assertTrue( os.path.isdir( os.path.join( d1.name(), d2.name())))
        
        shutil.rmtree( d1.name())
        
        with RandomDir() as d1 :
            with RandomDir( d1.name())  as d2 :
                self.assertTrue( os.path.isdir( os.path.join( d1.name(), d2.name())))
                
        self.assertFalse(os.path.isdir( os.path.join( d1.name(), d2.name())))
        
    def testRandomFile(self):
        
        r = RandomFile(size = 0 )
        self.assertTrue( os.path.isfile( r.name()))
        
        r = RandomFile(size = 1024)
        self.assertTrue( os.path.isfile( r.name()))
        self.assertEqual(os.path.getsize(r.name()), 1024)
        
        self.assertEqual( r.name(), os.path.join( r.dirname(), r.basename()))
        r.rm()
        self.assertFalse(os.path.isfile(r.name()))
        
    def testRandomFileName(self):
        f = RandomFile(  size = 1024 * 1024 )
        self.assertEqual(os.path.getsize(f.name()), 1024 * 1024 )
        f.rm()
        self.assertFalse(os.path.isfile(f.name()))
 
        
    def testRandomFile1024(self, size = 1024):
        r = RandomFile(size = 1024 )
        self.assertEqual(os.path.getsize( r.name()), r.size())
        r.rm()
        
        self.assertFalse(os.path.isfile( r.name()))
        
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
        
    def randomTree(self, pre, suf, size, width, depth ):
        dCount = 0
        tsize  = 0
        fCount = 0
         
        randRoot = RandomName().basename()
        t = RandomTree( randRoot, prefix=pre, suffix=suf)
        ( dirCount, fileCount, size ) = t.makeRandomTree( size, width, depth )
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
        
        self.randomTree( pre="", suf="", size=0, width=1, depth=1)
        
        self.randomTree( pre="123", suf="", size=1, width=1, depth=1)
        
        self.randomTree( pre="123", suf="", size=1, width=2, depth=1)
        
        self.randomTree( pre="123", suf="XYZ", size=243, width=3, depth=2)
        
        self.randomTree( pre="123", suf="XYZ", size=243, width=3, depth=2)
        
        
if __name__ == '__main__':
    unittest.main()