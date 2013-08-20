'''
Created on Aug 20, 2013

@author: jdrumgoole
'''

import argparse
import os
from filetools import filestat
from filetools.checksum import Checksum
import requests
import socket
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument( "-p", "--putone", 
                         dest="onefile",
                         help="add a single file to the DB")
    
    # Process arguments
    args = parser.parse_args()
    
    onefile=args.onefile
    
    if onefile:
        path = os.path.abspath( onefile )
        statInfo = filestat.FileStat( path )
        
        checksum = 0
        
        cs = Checksum()
        
        if statInfo.isdir() :
            checksum = 0
        else:
            checksum = cs.blockComputeFile( path )
        
        payload =  { "host"     : socket.gethostname(),
                     "path"     : path,
                     "filename" : os.path.basename( path ),
                     "size"     : statInfo.size(),
                     "ctime"    : statInfo.ctime(),
                     "atime"    : statInfo.atime(),
                     "mtime"    : statInfo.mtime(),
                     "isdir"    : statInfo.isdir(),
                     "checksum" : checksum }
        
        headers = {'content-type': 'application/json'}
        
        requests.post( "http://localhost:8080/add", 
                       data=json.dumps( payload ),
                       headers=headers )