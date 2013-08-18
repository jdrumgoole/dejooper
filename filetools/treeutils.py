'''
Created on 12 Jun 2009

@author: jdrumgoole
'''

import os
import itertools
from filetools.fileutils import FileOps


class TreeUtils :

    def __init__(self ):   
        pass
            
    def list(self, path, filesSelector=None, dirsSelector=None, topDown=True ):
            
        if dirsSelector  and topDown :
            yield path
            
        for root, dirs, files in os.walk( path, topdown = topDown ):
            if ( dirsSelector ) :
                dirs.sort()
                #yield( _root )
                for d in dirs :
                    yield( os.path.join( root, d ))
            if ( filesSelector ):
                files.sort()
                for f in files :
                    yield( os.path.join( root, f ))

        if dirsSelector and not topDown :
            yield path
           
    def listAll(self, path, topDown=True):
        for f in self.list( path, filesSelector=True, dirsSelector=True, topDown = topDown ):
            yield( f )
            
    def listFiles(self, path, topDown=True):  
        for f in self.list( path, filesSelector=True, topDown = topDown ) :
            yield ( f )
                 
    def listDirs( self, path, topDown = True ):
        for d in self.list( path, dirsSelector=True, topDown = topDown ) :
            yield ( d )

    def sizes(self, path ):
        for f in self.listFiles( path ) :
            yield os.path.getsize( f )
              
    def compare(self, path1, path2 ):
        '''
        Compare  path1 and path2 to see if they are identical
        '''
        
        matchFails = []
        
        matchCount = 0
        fo = FileOps()
        

        for lhs, rhs  in itertools.izip_longest( self.listAll(path1), self.listAll( path2 ), fillvalue = None ):
            matchCount = matchCount + 1
            if matchCount == 1 :
                # allow us to compare to trees with different root names
                # we skip the first match
                continue 


            if not fo.isEqual( lhs, rhs ) :
                matchFails.append(( lhs, rhs ))

        return matchFails
    
             
    def data(self, path ): 
        size = 0
        fileCount = 0
        dirCount = 0 # root dir counts a 1.
        
        for f in self.listAll( path ) :
            #print "TreeList : %s" % f
            if os.path.isdir( f ):
                dirCount = dirCount + 1
            elif os.path.isfile( f ) :
                fileCount = fileCount + 1
                size = size + os.path.getsize( f )
            else:
                raise IOError( "file does not exist : %s " % f )
                
        return( dirCount, fileCount, size )


    #
    # Copy a src dir to a target dir with all subdirs.
    # Before src/*,dest
    # After src/*, dest/src/*
    
    def copy(self, src, dest ) :
    
       
        fo = FileOps()
        src_a = os.path.abspath( src )
        dest_a = os.path.abspath( dest )
        
        # print "copy %s %s" % ( src_a,  dest_a )
        if not os.path.isdir( src_a ):
            raise ValueError( "the  source directory \'%s\' does not exist" % src_a )
        
        if not os.path.isdir( dest_a ):
            fo.makedir( dest_a )
        
        new_root = os.path.join( dest_a, os.path.basename( src_a ))
        
        #print "copy: makedir : %s" % new_root
        fo.makedir( new_root )
        
        for root, dirs, files in os.walk( src_a ):
            for d in dirs:
                # print "copy: makedir : %s" % os.path.join( new_root, d )
                fo.makedir( os.path.join( new_root, d ))
            for f in files:
                # print "copy: copyfile : %s %s" % ( os.path.join( root, f ), os.path.join( new_root, f ))
                fo.copyfile( os.path.join( root, f ), 
                             os.path.join( new_root, f ))
         
    def rm( self, path  ):
        
        for i in self.listFiles( os.path.abspath( path )) :
            #print "rm : %s" %i
            os.unlink(i)

        for i in self.listDirs( os.path.abspath( path ), topDown=False ) :
            #print "rmdir %s" % i
            os.rmdir(i) 
            
        self._dirs = []
        self._files = []
        self._totalSize = 0
