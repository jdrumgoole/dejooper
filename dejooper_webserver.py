from bottle import route, run, get, request, template
import logging
import argparse

from filescollection import FilesCollection

class DejooperWebServer :
    
    def __init__(self, name="dejooper", host='localhost', level=logging.DEBUG):
        self._name = name 
        logging.basicConfig(filename=name+".log", format=logging.BASIC_FORMAT)
        self._log=logging.getLogger( name )
        self._log.setLevel( level )
        self._log.info( name + " instantiated" )
        self._files = FilesCollection( host=host, dbname="filemetadata")



@get('/duplicates')
def duplicates():
    log = logging.getLogger( "dejooper")
    fc = FilesCollection( dbname="filemetadata")
    log.info( "Called duplicates")
    return template( "duplicates", filesCollection=fc)
    
@get('/get/:checksum' )
def get( checksum ) :
    log = logging.getLogger( "dejooper")
    log.info( "Called: get" )
    files = FilesCollection( dbname="filemetadata")
    f = files.getFileByChecksum(checksum)
    return f['path']


@route('/add', method='POST')
def add():
    log = logging.getLogger( "dejooper")
    log.info( "Called: add" )
    log.info( "request json %s:" % request.json )
    files = FilesCollection( dbname="filemetadata")
    files.addFileFromWeb( request.json )
    return "All Ok" 

parser = argparse.ArgumentParser()

parser.add_argument( "-x", "--dbhost", 
                     dest="dbHost",
                     default="localhost",
                     help="server to use")

args = parser.parse_args()
  
server=DejooperWebServer(host =args.dbHost )

run(host='0.0.0.0', port=8080, debug=True)
