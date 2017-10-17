from flask import (Flask, render_template, request, redirect,
                   jsonify, url_for, flash)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import scoped_session, sessionmaker
from models.models import Base, User, Category, Book
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
app.secret_key = 'super_secret_key'


CLIENT_ID = json.loads(
    open('/var/www/html/bookshelf/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "bookshelf-glaser"

# Connect to Database and create database session
engine = create_engine('sqlite:///bookshelfdatabase.db', connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine

session_factory = sessionmaker(bind=engine)
# Need scoped session in order to avoid cross threading with SQLite3
Session = scoped_session(session_factory)
session = Session()


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Main Page
@app.route('/')
@app.route('/bookshelf')
def showBookshelf():
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('publicMain.html',
                               categories=categories)
    else:
        return render_template('main.html', categories=categories)


#  Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect(url_for('showBookshelf'))
    user_id = login_session['user_id']
    creator = getUserInfo(user_id)
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        # TODO: add user_id=login_session['user_id'] above
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showBookshelf'))
    else:
        return render_template('newCategory.html', creator=creator)


# Display the contents of a category
@app.route('/bookshelf/<int:category_id>')
@app.route('/bookshelf/<int:category_id>/list/')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    books = session.query(Book).filter_by(
        category_id=category_id).all()
    #  Checks Authorization to view
    if 'username' not in login_session or creator.id != login_session[
            'user_id']:
        return render_template('publicBooks.html', books=books,
                               category=category, creator=creator)
    else:
        return render_template('categoryBooks.html', books=books,
                               category=category, creator=creator)


# Edit a category
@app.route('/bookshelf/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(
        id=category_id).one()
    creator = getUserInfo(editedCategory.user_id)
    #  Checks whether user is logged-in
    if 'username' not in login_session:
        return redirect('/login')
    #  checks whether current user is authorized to edit
    if editedCategory.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert('Your are not authorized
            to edit this subject. Please create your own subject in
            order to edit it.');}</script><body onload='myfunction()''>"""
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        flash('Category Successfully Edited %s' % editedCategory.name)
        return redirect(url_for('showCategory',
                                category_id=category_id, creator=creator))
    else:
        return render_template('editCategory.html',
                               category=editedCategory, creator=creator)


@app.route('/bookshelf/delete/<int:category_id>',
           methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(
        id=category_id).one()
    creator = getUserInfo(categoryToDelete.user_id)
    #  Checks whether User is logged-in
    if 'username' not in login_session:
        return redirect('/login')
    #  Checks whether User is authorized to delete the category
    if categoryToDelete.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert('Your are not authorized
            to delete this subject. Please create your own subject in
            order to delete it.');}</script><body onload='myfunction()''>"""
    if request.method == 'POST':
        booksToDelete = session.query(Book).filter_by(
            category_id=category_id).all()
        #  Deletes all the books within the category
        for b in booksToDelete:
            session.delete(b)
        #  Deletes the category
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showBookshelf'))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete, creator=creator)


#  Create a new book
@app.route('/bookshelf/<int:category_id>/book/new/',
           methods=['GET', 'POST'])
def newBook(category_id):
    user_id = login_session['user_id']
    creator = getUserInfo(user_id)
    category = session.query(Category).filter_by(id=category_id).one()
    #  Checks whether a User is logged-in
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBook = Book(title=request.form['title'],
                       description=request.form['description'],
                       author=request.form['author'],
                       category_id=category_id,
                       user_id=category.user_id)
        session.add(newBook)
        session.commit()
        flash('New Book %s Successfully Created' % (newBook.title))
        return redirect(url_for('showCategory', category_id=category_id,
                        creator=creator))
    else:
        return render_template('newBook.html', category_id=category_id,
                               creator=creator)


@app.route('/bookshelf/<int:category_id>/book/<int:book_id>/edit',
           methods=['GET', 'POST'])
def editBook(category_id, book_id):
    editedBook = session.query(Book).filter_by(id=book_id).one()
    creator = getUserInfo(editedBook.user_id)
    #  Checks whether User is logged-in
    if 'username' not in login_session:
        return redirect('/login')
    #  Checks whether User is authorized to edit the book
    if editedBook.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert('Your are not authorized
            to edit this book. Please create your own book in
            order to edit.');}</script><body onload='myfunction()''>"""
    if request.method == 'POST':
        if request.form['title']:
            editedBook.title = request.form['title']
        if request.form['description']:
            editedBook.description = request.form['description']
        if request.form['author']:
            editedBook.author = request.form['author']
        session.add(editedBook)
        session.commit()
        flash('Book Successfully Edited')
        return redirect(url_for('showCategory', category_id=category_id,
                        creator=creator))
    else:
        return render_template('editBook.html',
                               category_id=category_id,
                               book_id=book_id,
                               book=editedBook,
                               creator=creator)


@app.route('/bookshelf/<int:category_id>/book/<int:book_id>/delete/',
           methods=['GET', 'POST'])
def deleteBook(category_id, book_id):
    bookToDelete = session.query(Book).filter_by(id=book_id).one()
    creator = getUserInfo(bookToDelete.user_id)
    #  Checks whether User is logged-in
    if 'username' not in login_session:
        return redirect('/login')
    #  Checks whether User is authorized to delete the book
    if bookToDelete.user_id != login_session['user_id']:
        return """<script>function myFunction() {alert('Your are not authorized
            to delete this book. Please create your own book in
            order to delete.');}</script><body onload='myfunction()''>"""
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash('Book Successfully Deleted')
        return redirect(url_for('showCategory', category_id=category_id,
                        creator=creator))
    else:
        return render_template('deleteBook.html', book=bookToDelete,
                               creator=creator)


""" The Following methods relate to the log-in/log-out process, the initial
login page shows an option to log-in through either Google or Facebook,
depending on which one the User chooses, the User gets routed to the
corresponding function below. Those functions then check to see if the
credentials which were entered match the credentials at either Facebook or
Google. If they match, the User is either newly created, or allowed to log-in.
If they do not match, then the User is not allowed to log-in"""


@app.route('/bookshelf/login')
def showLogin():
    state = ''.join(random.choice(
            string.ascii_uppercase + string.digits)for x in range(32))
    login_session['state'] = state
    return render_template('/login.html', STATE=state)


@app.route('/disconnect')
def disconnect():
    #  Determines which provider the user used to log-in and redirects
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        #  Clears login_session
        login_session.clear() ## can also .pop() each indiv attribute

        flash("You have successfully been logged out.")
        return redirect(url_for('showBookshelf'))
    else:
        flash("You were not logged in to begin with!")
        redirect(url_for('showBookshelf'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/html/bookshelf/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?'
           'access_token=%s' % access_token)

    h = httplib2.Http()
    str_response = h.request(url, 'GET')[1]
    result = json.loads(str_response.decode()) # JSON won't take  info without decode()
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                   'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

# see if user exits, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'
    output += '150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
                   'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke'
           '?token=%s' % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                   'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
           facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# facebook function in /login.html makes an AJAX call here and  sends 'data'
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode() # Data must be decoded to be the right type
    app_id = json.loads(open('/var/www/html/bookshelf/fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('/var/www/html/bookshelf/fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           + 'fb_exchange_token&client_id=%s&' % app_id
           + 'client_secret=%s&' % app_secret
           + 'fb_exchange_token=%s' % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    token = result.decode().split(',')[0].split(':')[1].replace('"', '')
    url = ('https://graph.facebook.com/v2.8/me?access_token='
           + '%s&fields=name,id,email' % token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode())
    # Put information from data into login_session
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?access_token='
           + '%s&redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode()) #JSON wont accept data in the original state
    login_session['picture'] = data["data"]["url"]

    # see if user exists in our database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
            -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


#  JSON APIs to view My Library Information
@app.route('/bookshelf/<int:category_id>/list/JSON')
def categoryBooksJSON(category_id):
    books = session.query(Book).filter_by(
        category_id=category_id).all()
    return jsonify(Books=[b.serialize for b in books])


@app.route('/bookshelf/<int:category_id>/list/<int:book_id>/JSON')
def bookJSON(category_id, book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(Book=book.serialize)


@app.route('/bookshelf/JSON')
def bookshelfJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
