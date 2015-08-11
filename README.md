# netcat

Simple implementation of good and old netcat in python.

TODO:
send commands

### Usage: ###

* File transfer server:

./pycat.py -u /tmp/fileToReceiv -p 6666 -l

* File transfer client:

./pycat.py -t localhost -p 6666 -u /tmp/fileToSend


