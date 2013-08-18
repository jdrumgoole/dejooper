'''
Created on 18 Nov 2010

@author: jdrumgoole
'''

class FeedBack :

    def __init__( self ) :
        pass

    def percentage( self, size, xfer ) :
        return float( xfer ) / float( size ) * 100


    def progress( self, name, size, xfer ) :
        '''
        name = name of the file
        size = size of the file
        xfer = amount transferred to date
        '''
        
        pass

class SimpleFeedback( FeedBack ) :

    def __init_(self ):
        pass
    
    def progress( self, name, size, xfer ) :
        '''
        Name of file being transferred
        Size of data being transferred
        Xfer transferred so far
        '''
        print "Transferred %i%% of %s" % ( self.percentage( size, xfer ),
                                           name)

    
