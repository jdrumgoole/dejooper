from bottle import route, run, get, post, request, template, SimpleTemplate
import logging


from filescollection import FilesCollection

class DejooperWebServer :
    
    def __init__(self, name="dejooper", level=logging.DEBUG):
        self._name = name 
        logging.basicConfig(filename=name+".log", format=logging.BASIC_FORMAT)
        self._log=logging.getLogger( name )
        self._log.setLevel( level )
        self._log.info( name + " instantiated" )
        self._files = FilesCollection( dbname="filemetadata")



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

server=DejooperWebServer()
run(host='0.0.0.0', port=8080, debug=True)
