#!/bin/sh -e


GROUP_NAME='onion-dir'
DAEMON_PATH='/usr/sbin/onion-dir'
RC_FILE_PATH='/etc/init.d/onion-dir'

echo "Stopping service"
service onion-dir stop

echo "Removing ‘$GROUP_NAME’ group"
groupdel $GROUP_NAME || true
echo "Removing daemon from ‘$DAEMON_PATH’"
rm $DAEMON_PATH  || true
echo "Removing rc file to ‘$RC_FILE_PATH’"
rm $RC_FILE_PATH || true
