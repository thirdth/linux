# Item Catalog Application
Source code for a python based website that allows users to keep track of categories and items within those categories. **Full Stack Web Developer
Nanodegree Program** from **Udacity**.

## Overview
This particular application allows users to keep track of their books as items categorized by their subjects. A user can log-in using either Facebook or Google authorization. Once logged in, a user can create, edit and delete subjects. The user can then create, edit, and delete books within those subjects.

Sujects and Books cannot be edited, or deleted by any user who is not the original creator, except that if a user created a category it can delete all the books within that category whether said user is the owner of those books or not.

## Set-up Instructions
1. This program is intended to be used from a command line environment utilizing
a virtual machine in order to create a local server-host environment.
2. You will need to set-up a virtual machine like Virtual Box, and a way to connect
to that virtual machine, like with Vagrant.
3. Instructions for set-up VirtualBox can be found [here](https://www.virtualbox.org/manual/https://www.vagrantup.com/intro/getting-started/ch01.html)
4. Instructions to download and set up Vagrant can be found [here](https://www.vagrantup.com/intro/getting-started/)
4. Prior to setting up Vagrant, download the files for the program onto your local machine.
5. Navigate to the folder containing these files and run `vagrant up` in order to
initialize your virtualMachine and connect to it through Vagrant. These files contain
a Vagrantfile that handles the set-up.
6. Once you have set-up Vagrant and Virtual Box you can utilize the database and
program through the command line in vagrant.
8. Navigate to the local folder that you set up Vagrant in, and run `vagrant.ssh`.
9. Navigate to your Bookshelf folder in the virtual machine through the Vagrant directory.
13. Run `python bookshelf.py` to start the program.
14. After the program is running in your virtual machine open your browser and navigate to `http://localhost:5000/bookshelf` where you will find the program running.
15. User will need to log-in through his or her Facebook or Google account in order to create, edit, or delete information, however, user may view the subjects and books within those subjects without logging-in.

## Known Issues
1. Although a user may not edit or delete books that were created by another user, if a user deletes a category that they are the creator or, it will delete all the books within that category whether the user "owns" them or not.
2. Sometimes, when the virtual machine has been running for an extended period of time, the log-in function cannot find graph.facebook.com. If this happens, simply re-load the virtual machine using `vagrant reload`.
