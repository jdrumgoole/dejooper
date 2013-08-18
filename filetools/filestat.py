import unittest
import os
import stat

from testtools.randomutils import RandomFileHere, RandomDir, RandomName

class FileStat :

    DIR  = "directory"
    CHR  = "character device"
    REG  = "regular file"
    BLK  = "block device"
    FIFO = "named pipe"
    LNK  = "symbolic link"
    SOCK = "socket"
    UNK  = "unknown"
    
    def __init__( self, filename ):
    
        self._f = filename
        
        if os.path.islink( self._f ) :
            self._stat = os.lstat( self._f )
        elif os.path.exists( self._f ) :
            self._stat = os.stat( self._f )
        else:
            raise OSError( "No such file : %s" % self._f )

        self._abs_f = os.path.abspath( self._f )
        
    def __call__(self):
        return self.name()
    
    def name(self):
        return self._f
    
    def mode(self):
        return self._stat[stat.ST_MODE]
    
    def isdir(self):
        return stat.S_ISDIR( self.mode())
    
    def isfile(self):
        return stat.S_ISREG( self.mode())
    
    def isSoftLink(self):
        return stat.S_ISLNK( self.mode())
        
    def filetype(self):
        mode = self.mode()
        if stat.S_ISREG( mode ):
            return self.REG
        elif stat.S_ISDIR( mode ):
            return self.DIR
        elif stat.S_ISLNK( mode ):
            return self.LNK
        elif stat.S_ISFIFO( mode ):
            return self.FIFO
        elif stat.S_ISCHR( mode ):
            return self.CHR
        elif stat.S_ISSOCK( mode ):
            return self.SOCK
        elif stat.S_ISBLK( mode ):
            return self.BLK
        else:
            return self.s_UNK
        
    def abspath(self):
        return self._abs_f 
    
    def atime(self):
        return self._stat[ stat.ST_ATIME ]
    
    def ctime(self):
        return self._stat[ stat.ST_CTIME ]
    
    def mtime(self):
        return self._stat[ stat.ST_CTIME ]
    
    def size(self):
        return self._stat[ stat.ST_SIZE ]
    
    def _str_(self):
        print( "%s, %s, %i"  ) % (self.name(), self.filetype(), self.size())
    
class TestFileStat( unittest.TestCase):
    
    def testSize( self ):
        f = RandomFileHere( size=2483 )
        st = FileStat( f.name())
        self.assertEqual( os.path.getsize( st.name()), st.size())
        f.rm()
        
    def testDir(self ):
        f = RandomDir()
        st = FileStat( f.name())
        self.assertEqual( os.path.getsize( f.name()), st.size())
        self.assertEqual( os.path.isdir( f.name()), st.isdir())
        os.rmdir( f.name())
        
    def testSymLink(self):
        with RandomDir() as f :
            n = RandomName()
            os.symlink( f(), n())
            self.assertTrue( os.path.exists( n()))
            self.assertTrue( os.path.islink( n()))
            fst = FileStat( n())
            nst = FileStat( f())
            self.assertTrue( fst.isSoftLink())
            self.assertFalse( nst.isSoftLink())
            os.unlink( n())
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
