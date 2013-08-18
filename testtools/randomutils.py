'''
Created on 30 Nov 2010

@author: jdrumgoole
'''

import tempfile
import os
import random
import string


class RandomName:
    '''
    Create random path name. If rootDir is not specified  create file in default
    location for OS.
    '''
    
    def __init__(self, rootDir=None) :
        t = tempfile.NamedTemporaryFile( dir = rootDir )
        self._filename = os.path.abspath( t.name )
        t.close()
    
    def name(self):
        return self._filename 
    
    def __call__(self):
        return self._filename
    
    def basename(self):
        return os.path.basename( self._filename )
    
    def dirname(self):
        return os.path.dirname( self._filename )

    def __repr__( self ) :
        return self._filename

    def __str__( self ) :
        return self.__repr__()


    
def randomBasename( path = None ):
    return RandomName( path ).basename()

def randomName( path = None ):
    return RandomName( path ).name()


    
# def randomDir( path = None ):
#         
#     n = randomName( path )
#     os.mkdir( n )
#     
#     return n

class RandomDir( object )  :

    def __init__(self, root=None ):
        
        if root == None :
            self._root = os.getcwd()
        elif os.path.isdir( root ):
            self._root = os.path.abspath( os.path.normpath( root ))
        else:
            raise ValueError( "%s is not a directory" %  root )
        
        self._name = RandomName( self._root ).name()
        os.mkdir( self._name )
        
    def __call__(self):
        return self._name
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb ):
        os.rmdir( self._name )
        
    def name(self):
        return self._name
    
    def path(self):
        return os.path.join( self._root, self._name )
    
    def rmdir(self):
        os.rmdir( self._name )
        
class RandomString( object ) :

    def __init__(self, population ):
        self._population = population

    def population(self):
        return self._population
    
    def random(self, size ):
        return "".join( [random.choice( self._population )  for _ in xrange( size )] )
        
    #
    # Generator to create a series of chunks os size chunksize. Return enough
    # chunks to create a file of "size" bytes.
    #
    def randomChunk(self, size, chunkSize ):
        
        if size == 0 :
            yield ""
        elif size < 0 :
            raise ValueError( "size (%i) is less than 0" % size )
        elif  chunkSize < 0 :
            raise ValueError( "Chunksize (%i) is less than 0" % chunkSize )
        else:
            
            if chunkSize == 0 :
                chunkSize = size
                
            chunks = size / chunkSize
            remnant = size % chunkSize
            
            
            for _ in range( chunks )  :
                yield( self.random( chunkSize )) 
                
            if remnant > 0 :
                yield( self.random( remnant ))          


class RandomFile( object ):      

    def __init__(self, rootDir=None, 
                 size = 0, 
                 chunk = 0, 
                 population = string.letters,
                 prefix = "",
                 suffix = "",
                 name = "" ):
        '''
        RootDir = Location to put files
        size = size of file
        chunk = chunkSize to write file in
        population  = which string elements to use
        prefix = file prefix
        suffix = file suffix
        name = Name of file to create
        '''
        
        self._size = size
        
        self._random = RandomString( population )
        
        if rootDir is None:
            rootDir = os.getcwd()

        #
        # Dp this because closing a temporary file causes it to be deleted
        # on some OS's (windows). There is a slight security race hazard here but this
        # is mainly for testing not production use.
        
        if name == "" :
            t = tempfile.NamedTemporaryFile( dir=rootDir )
            t.close()
            self._filename = os.path.normpath(t.name )
        else:
            self._filename = name
        
        fDir = os.path.dirname( self._filename )
        base = os.path.basename( self._filename )
        
        base = "%s%s%s" % ( prefix, base, suffix )
        
        self._filename = os.path.join( fDir, base )
        
        with open( self._filename, "wb") as f:
            for i in self._random.randomChunk( size, chunk ):
                f.write( i )
    
    def __call__(self):
        return self._filename
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb ):
        self.rm()
    
        
    def basename(self):
        return os.path.basename( self._filename )
    
    def dirname(self):
        return os.path.dirname( self._filename )
    
    def name(self):
        return self._filename
    
    def size(self):
        return self._size
    
    def rm(self):
        os.unlink(self._filename)
        
class RandomFileHere( RandomFile ):
    
    def __init__(self, 
                 size = 512, 
                 chunk = 0, 
                 population = string.letters,
                 prefix = "",
                 suffix = "",
                 name = "" ):
        
        super( RandomFileHere, self ).__init__( rootDir = os.getcwd(),
                                                size = size,
                                                chunk = 0,
                                                population = population,
                                                prefix=prefix,
                                                suffix=suffix,
                                                name = name )
            
        
        
