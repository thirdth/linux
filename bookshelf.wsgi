import sys
sys.path.insert(0,"/var/www/html/")
sys.path.append('/var/www/html/bookshelf/')
sys.path.append('/var/www/html/bookshelf/models')
sys.path.append('/var/www/html/bookshelf/templates')
sys.path.append('/var/www/html/bookshelf/static')
from bookshelf.app import app as application
