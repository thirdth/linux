# Linux Server Set-up
The following are the set-up parameters for a Linux server running on Amazon AWS Lightsail servers. This is a project for **Full Stack Web Developer Nanodegree Program** from **Udacity**. The server is intended to be set-up in such a way that it will host a previous python project from the **Udacity** program.

## Grader connection information
1. **IP Address and SSH port** = 52.14.79.23:2200
2. **URL** = [52.14.79.23/bookshelf.html](52.14.79.23/bookshelf.html)
3. **Login ID** Grader
4. **Public Key** = in notes


## Project Information

* **Installed Software**
  1. Finger
  2. Apache2
  3. mod_wsgi for python3
  4. Flask
  5. sqlalchemy
  6. Oauth2
  7. SQLite3


* **Summary of Configurations Made**
  1. General Configurations
    - Changed timezone to UTC
  1. User management & File Permissions:
    - Remote access for root user turned off.
    - New user "Grader" created.
    - "Grader" given sudo permission (/etc/sudoers.d/grader)
    - Created key pair
    - Edited `/.ssh/authorized_keys` to add Key
    - Changed file permissions on `/.ssh` & `/.ssh/authorized_keys` to 700 and 644 respectively
    - Disabled password based login with `/etc/ssh/sshd_config`
    - Disabled remote login as root user
    - Once application was installed, I made the user "www-data" the owner of the files the application was in so SQLite3 could create and edit the database using the `chown` command.
  3. Firewall & Ports:
    - Denied all incoming
    - Allowed all outgoing
    - Configured UFW to open ports:
      - 2200 for SSH
      - 80 for HTTP
      - 123 for NTP
  4. Apache Configurations:
    - Installed Apache2
    - Installed mod_wsgi for python3
    - Edited `/etc/apache2/sites-enabled/000-default.conf` in order to serve `bookshelf.wsgi` when a request is made to the server.
    - Edited `bookshelf.wsgi` so it knew where to look for files.
      - read a lot of answers and articles by Graham Dumpleton
    - Edited `bookshelf.wsgi` so it loaded the application from `app.py`
  5. Application Configurations
    - Created a python virtual env in order to control which python was used.
    - Edited `/etc/apache2/sites-enabled/000-default.conf` to point to the proper python path.
    - Installed the software that the app is reliant on (as above).
    - Used `scoped_session` to get around the cross thread problem of using SQlite.


* **Third Party Resources**
  1. Amazon Lightsail
  - Apache2
  - mod_wsgi
  - Google Oauth2
  - Facebook Oauth2
