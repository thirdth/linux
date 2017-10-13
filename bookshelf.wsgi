import sys
sys.path.insert(0,"/var/www/html/")
sys.path.append('/var/www/html/bookshelf/')
sys.path.append('/var/www/html/bookshelf/models')
sys.path.append('/var/www/html/bookshelf/templates')
sys.path.append('/var/www/html/bookshelf/static')
from bookshelf.app import app as application

#def application(environ, start_response):
#    status = '200 OK'

#    output = u''
#    output += u'sys.version = %s\n' % repr(sys.version)
#    output += u'sys.prefix = %s\n' % repr(sys.prefix)
#    output += u'sys.path = %s\n' % repr(sys.path)

#    response_headers = [('Content-type', 'text/plain'),
#                        ('Content-Length', str(len(output)))]
#    start_response(status, response_headers)

#    return [output.encode('UTF-8')]
