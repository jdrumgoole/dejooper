'''
Created on Jul 19, 2013

@author: jdrumgoole
'''
from duplicatefiledb import DuplicateFileDB, FilesCollection
import pymongo

if __name__ == '__main__':
    
    try :
        m = DuplicateFileDB()
    except ( pymongo.errors.ConnectionFailure ) as e :
        print "%s : Is the mongo deaemon running?" %e
        exit(1)
        
    f = FilesCollection( m.db())
    
    f.findDupes()
    
