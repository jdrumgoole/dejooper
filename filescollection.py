'''
Created on May 29, 2013

@author: jdrumgoole
'''

import pymongo
from bson import binary
import os
from filetools.filestat import FileStat
from filetools import checksum
import unittest
from testtools import randomutils
from basetools import debug,timer
from filetools.checksum import Checksum
import shutil
import socket
import requests


class FilesCollection :
    '''
    FilesCollection contains two collections the first is a list of all the files 
    that we have scanned.
    
    The second is a duplicates list which is a list of all the files with a checksum 
    that is matched to more than one file in the files collections list.
    '''

    def __init__(self, collectionName = "fc", dbname="DuplicateFileDB", port=27017 ):

        self._db = dbname
        self._collectionName = collectionName
        self._duplicatesName = self._collectionName + "_duplicates"

        self._client = pymongo.MongoClient('localhost', port )
        self._db = self._client[ self._db ]
        
        self._filesCollection = self._db[ self._collectionName ]
        self._checksum = checksum.Checksum()
        
        self._duplicates = self._db[ self._collectionName +'_duplicates']
        
        self._filesCollection.create_index( 'path' )
        self._filesCollection.create_index( "checksum" )
        self._filesCollection.create_index( 'ctime' )
           
        self._duplicates.create_index( 'path'  )
        self._duplicates.create_index( "checksum", unique=True )

           
    def client(self):
        return self._client
        
    def db(self):
        return self._db
    
    def dropDB(self):
        return self._client.drop_database( self._db )
    
    def dropCollections(self):
        self._db.drop_collection( self._collectionName )
        self._db.drop_collection( self._duplicatesName )
        
    def count(self):
        return self._filesCollection.count()
    
    def duplicatesCount(self):
        return self._duplicates.find().count()
    
    def allDuplicates(self):
        for d in self._duplicates.find() :
            yield ( d[ 'path'], d['checksum'] )
            
    def getDuplicates(self, path, checksum ):
        
        if self.inDuplicates( checksum ) :
            dupes = self._filesCollection.find( {'checksum' : checksum })
            
            dupes.sort( "ctime", pymongo.ASCENDING )
            
            for d in dupes :
                if path != d['path']:
                    yield ( d['host'], d['path'], d['ctime'] )

    
    def allfiles(self):
        for f in self._filesCollection.find():
            yield f
            
    def allPaths(self):
        for f in self._filesCollection.find():
            yield f[ 'path']

    def getFileByPath(self, path ):
        return self._filesCollection.find_one( { "path" : path })
    
    def getFileByID(self, fileID):
        return self._filesCollection.find_one( { "_id": fileID })
    
    def getFileByChecksum(self, checksum):
        return self._filesCollection.find_one( { "checksum": checksum })
    
    def inFilesCollection(self, path ):
        return self._filesCollection.find_one( {"path" : path })
    
    def inDuplicates(self, checksum ):  
        return ( self._duplicates.find_one( {"checksum" : checksum }) != None )
    
    def hasDuplicates(self, checksum ):
        return self._filesCollection.find( {"checksum": checksum }).count() > 1 
    
    def pathInDuplicates(self, path ):  
        return ( self._duplicates.find_one( {"path" : path }) != None )
    
    def validFile(self, path ):
        fs = None
        try :
            fs = FileStat( path )
        except ( OSError ):
            return None
        
        if fs.isSoftLink():
            return None
        
        return fs
       
    def addFileToDb(self, statInfo, path ):
        
        if statInfo.isdir() :
            checksum = 0
        else:
            checksum = self._checksum.blockComputeFile( path )

        payload =  { "host"     : socket.gethostname(),
                     "path"     : path,
#                     "header"   : binary.Binary( statInfo.header()),
                     "filename" : os.path.basename( path ),
                     "size"     : statInfo.size(),
                     "ctime"    : statInfo.ctime(),
                     "atime"    : statInfo.atime(),
                     "mtime"    : statInfo.mtime(),
                     "isdir"    : statInfo.isdir(),
                     "checksum" : checksum }
        
        self._filesCollection.insert( payload )
        
        return checksum
    
    def updateFileInDb(self, statInfo, path ):
        
        if statInfo.isdir() :
            checksum = 0
        else:
            checksum = self._checksum.blockComputeFile( path )
            
        self._filesCollection.update( {"path" : path },
                                      { "host"     : socket.gethostname(),
                                        "path"     : path,
#                                        "header"   : binary.Binary( statInfo.header()),
                                        "filename" : os.path.basename( path ),
                                        "size"     : statInfo.size(),
                                        "ctime"    : statInfo.ctime(),
                                        "atime"    : statInfo.atime(),
                                        "mtime"    : statInfo.mtime(),
                                        "isdir"    : statInfo.isdir(),
                                        "checksum" : checksum },
                                        upsert=True )    
        return checksum
    
    def addToDuplicates(self, size, checksum, path ):
        dupeCount = self._filesCollection.find( { "checksum" : checksum }).count()
        
        if dupeCount > 1 :
            self._duplicates.update( { "checksum" : checksum },
                                     { "path" : path, 
                                      "checksum" : checksum,
                                      "size" : size },
                                     upsert=True )
            
    def addFileFromWeb(self, payload ):
        
        self._filesCollection.update( {'path' : payload[ 'path']}, payload, upsert=True )
                
        if  ( not payload[ 'isdir' ] ) and self.hasDuplicates( payload[ 'checksum'] ) :
            self.addToDuplicates( payload[ 'checksum'], payload['path'] )
            
        return checksum
    
    def addFile(self, path ):
        
        checksum = 0
        
        statInfo = self.validFile(path)
        
        if statInfo is None :
            return
        
        existingFile = self.inFilesCollection(path)
        
        if existingFile:
            if self.isSameFile( statInfo, existingFile ):
                checksum = existingFile[ 'checksum']
            else:
                checksum = self.updateFileInDb(statInfo, path)
        else:
            checksum = self.addFileToDb( statInfo, path )
          
        
        if  statInfo.isfile() and self.hasDuplicates( checksum ) :
            self.addToDuplicates( statInfo.size(), checksum, path )
            
        return checksum
      
    def sameFilename(self, name ):
        filesCursor = self._filesCollection.find({ "filename" : name}).sort( "filename", pymongo.ASCENDING)
              
        for f in filesCursor :
            yield f[ 'path ']
        
    def sizes(self, greaterThan, lessThan ):
            
        filesCursor = self._filesCollection.find( { "size" : { "$gt": greaterThan, "$lt" : lessThan }})
        for f in filesCursor :
            yield ( f[ 'path'], f['size'] )
        
    def sameFilenames(self):
        
        
        filesCursor = self._filesCollection.find().sort( "filename", pymongo.ASCENDING)
        
        for f1 in filesCursor :
            #print "f1 %s" % f1["filename"]
            for f2 in filesCursor :
                #print "f2 %s" % f2['filename']
                if f2['filename' ]  == f1['filename'] :
                    #print "samefile"
                    yield ( f2['path'])
                else:
                    break
                

    def isSameFile(self, fs, dbInfo):
        #
        #If the file is the same size, has the same path and the same mtime and ctim
        # as the file in the db we assume its the same file in which case we don't 
        # need to update the db or recalculate the checksum.
        #
        
        return (( fs.size()  == dbInfo[ 'size' ] ) and
                ( fs.ctime() == dbInfo[ 'ctime'] ) and
                ( fs.mtime() == dbInfo[ 'mtime'] ) and
                ( fs.name()  == dbInfo[ 'path' ] ))
        
    
    def filesCollection(self):
        return self._filesCollection
    
class testFileDB( unittest.TestCase ):
    
    def setUp(self):
        self._fc= FilesCollection( dbname="fctest", collectionName = "fctest")
        
    def tearDown(self):
        self._fc.dropCollections()
        self._fc.dropDB()
        
    def testAddDir(self):
        d = randomutils.RandomDir()
        
        self._fc.addFile(d())
        self.assertTrue( self._fc.inFilesCollection( d()))
        
        d.rmdir()
        
    def testAddFile(self):
        
        f = randomutils.RandomFileHere( 1024 )
        self._fc.addFile( f())

        fRec = self._fc.getFileByPath( f())
        self.assertIsNotNone( fRec )
        self.assertEqual( os.path.getsize( f.name()), fRec[ 'size' ] )
        self.assertTrue( self._fc.inFilesCollection( f()))
        self.assertTrue( self._fc.isSameFile( FileStat( f.name()), fRec ))
        self.assertEqual( 1, self._fc.count())
        self.assertEqual(0, self._fc.duplicatesCount())
        f.rm()

    def testAddFromWeb(self):
        
        f = randomutils.RandomFileHere( 1024 )
        c =Checksum()
        checksum = c.blockComputeFile(f())
        statInfo = FileStat(f())
        
        payload =  { "host"     : socket.gethostname(),
                     "path"     : f(),
                     "filename" : os.path.basename(f()),
                     "size"     : statInfo.size(),
                     "ctime"    : statInfo.ctime(),
                     "atime"    : statInfo.atime(),
                     "mtime"    : statInfo.mtime(),
                     "isdir"    : statInfo.isdir(),
                     "checksum" : checksum }
                  
        self._fc.addFileFromWeb( payload )

        fRec = self._fc.getFileByPath( f())
        self.assertIsNotNone( fRec )
        self.assertEqual( os.path.getsize( f.name()), fRec[ 'size' ] )
        self.assertTrue( self._fc.inFilesCollection( f()))
        self.assertTrue( self._fc.isSameFile( FileStat( f.name()), fRec ))
        self.assertEqual( 1, self._fc.count())
        self.assertEqual(0, self._fc.duplicatesCount())
        f.rm()
        
        
    def testAddTwoFiles(self):
        f1 = randomutils.RandomFileHere( 1024 )
        f2 = randomutils.RandomFileHere( 1024 )
        
        self._fc.addFile( f1())
        self._fc.addFile( f2())
        self.assertTrue( self._fc.inFilesCollection( f1()))
        self.assertTrue( self._fc.inFilesCollection( f2()))
        self.assertEqual( 2, self._fc.count())
        f1.rm()
        f2.rm()
        
    def testSizes(self):
        f1 = randomutils.RandomFileHere( 1000 )
        f2 = randomutils.RandomFileHere( 1500 )
        
        self._fc.addFile( f1())
        self._fc.addFile( f2())
        sizeList = []
        for x in self._fc.sizes( 200, 2000 ):
            sizeList.append( x )
            
        self.assertEqual( len( sizeList ), 2 )
            
        f1.rm()
        f2.rm()
        
        
    def testAddDuplicate(self):
        f = randomutils.RandomFileHere( 1024 )
        fCopy = f() + "1"
        shutil.copyfile( f(), fCopy )
        c = self._fc.addFile( f())
        self._fc.addFile( fCopy )
        self.assertTrue( self._fc.getFileByPath( f()))
        self.assertTrue( self._fc.getFileByPath( fCopy ))
        self.assertTrue( self._fc.getFileByChecksum( c ))
        self.assertTrue( self._fc.inDuplicates( c ))
        self.assertTrue( self._fc.pathInDuplicates( fCopy ))
        self.assertEqual( 1, self._fc.duplicatesCount())
        
        dupes = self._fc.allDuplicates()
        
        for (path1, checksum1 )  in dupes:
            copies = self._fc.getDuplicates(path1, checksum1)
            for ( path2, _ ) in copies:
                self.assertNotEqual( path1, path2 )
        f.rm()
        os.unlink( fCopy )
        
    def testInCollection(self ):
        
        f = randomutils.RandomFileHere( 1024 )
        self._fc.addFile( f())
        self.assertTrue( self._fc.inFilesCollection( f() ))
        f.rm()
        
    def testBadSymLink(self):
        target = randomutils.RandomName()
        src = randomutils.RandomDir()
        os.symlink( src.name(), target.name())
        os.unlink( target.name())
        self._fc.addFile( src.name())
        os.rmdir( src.name())
        
    def testSpecificSymlink(self):
        path = '/Users/jdrumgoole/.npm/findit/0.1.2/package/test/symlinks/dir1/dangling-symlink'
        self._fc.addFile( path )
        
if __name__ == "__main__" :
    unittest.main()
    
           
