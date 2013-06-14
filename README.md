Onion-Dir
=========

Resolve names through [Tor](https://www.torproject.org/) so no one listening
the network nor even the ISP sniffs it.

Resolution is done using the [Tor proxy interface](http://download.exdat.com/viewprogramfile/18551-22).


Dependencies
------------

Onion-Dir depends upon [twisted](http://twistedmatrix.com/), may be installed
through [pip](https://pypi.python.org/pypi) with the command:

`pip install twisted`


Usage
-----

Syntax: `onion-dir.py (-f|-d) [-p <pidfile>] [-h]`

-f: Launch in foreground  
-d: Launch in the background (default)  
-p: Save the process ID in the specified file  
-h: Show this help and exit  
