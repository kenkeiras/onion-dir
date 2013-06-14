#!/bin/sh -e


GROUP_NAME='onion-dir'
DAEMON_PATH='/usr/sbin/onion-dir'
RC_FILE_PATH='/etc/init.d/onion-dir'

echo "Creating ‘$GROUP_NAME’ group"
groupadd $GROUP_NAME || true
echo "Copying daemon to ‘$DAEMON_PATH’"
install onion-dir.py $DAEMON_PATH  || true
echo "Copying rc file to ‘$RC_FILE_PATH’"
install onion-dir.rc $RC_FILE_PATH || true

echo "Starting service"
service onion-dir start
