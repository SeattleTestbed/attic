#!/bin/bash

# Ths will update the base installers used by seattelgeni from what
# is currently checked out as trunk. See constants below.
#
# You will need sudo privileges to use this. Don't run this as sudo, it will
# invoke sudo when it needs it.
#
# Usage: ./rebuild_base_installers_for_seattlegeni.sh VERSION_STRING

VERSION=$1

SOFTWARE_UPDATE_URL=http://betaseattleclearinghouse.poly.edu/updatesite/
PUBLIC_KEY_FILE=/root/beta-testbed-softwareupdater-keys/beta-testbed-softwareupdater.publickey

e=`cat $PUBLIC_KEY_FILE | cut -d' ' -f 1`
n=`cat $PUBLIC_KEY_FILE | cut -d' ' -f 2`
SOFTWARE_UPDATE_KEY="{'e':$e, 'n':$n}"

SVN_TRUNK_DIR=/home/release/repy_v2/

#BASE_INSTALLER_DIRECTORY=/home/custominstallerbuilder/live/custominstallerbuilder/html/static/installers/base
BASE_INSTALLER_DIRECTORY=/var/www/html/dist/
BASE_INSTALLER_ARCHIVE_DIR=/var/www/html/dist/old_base_installers

SOFTWARE_UPDATE_SERVER=/var/www/html/updatesite/

if [ "$VERSION" == "" ]; then
  echo "You must supply a version string."
  echo "usage: $0 version"
  exit 1
fi

if [ "$SOFTWARE_UPDATE_URL" == "" ]; then
  echo "SOFTWARE_UPDATE_URL isn't set."
  exit 1
fi

if [ ! -d "$BASE_INSTALLER_DIRECTORY" ]; then
  echo "BASE_INSTALLER_DIRECTORY doesn't exist."
  exit 1
fi

if [ ! -d "$BASE_INSTALLER_ARCHIVE_DIR" ]; then
  echo "BASE_INSTALLER_ARCHIVE_DIR doesn't exist."
  exit 1
fi

if [ ! -d "$SVN_TRUNK_DIR" ]; then
  echo "SVN_TRUNK_DIR doesn't exist."
  exit 1
fi

if [ "`grep -F "$VERSION" $SVN_TRUNK_DIR/nodemanager/nmmain.py`" == "" ]; then
  echo "You need to set the version string in $SVN_TRUNK_DIR/nodemanager/nmmain.py"
  exit 1
fi

UPDATE_URL_FOUND=$(grep -F "softwareurl = \"$SOFTWARE_UPDATE_URL\"" $SVN_TRUNK_DIR/softwareupdater/softwareupdater.py)

if [ "$UPDATE_URL_FOUND" == "" ]; then
  echo "Did not find the correct update url in $SVN_TRUNK_DIR/softwareupdater/softwareupdater.py"
  exit 1
fi


echo "Archiving old base installers to $BASE_INSTALLER_ARCHIVE_DIR"
echo "Warning: failure after this point may leave seattlegeni with no base installers!"
sudo mv -f $BASE_INSTALLER_DIRECTORY/seattle_* $BASE_INSTALLER_ARCHIVE_DIR

echo "Building new base installers at $BASE_INSTALLER_DIRECTORY"
sudo python $SVN_TRUNK_DIR/dist/make_base_installers.py \
  a \
  $SVN_TRUNK_DIR \
  /root/beta-testbed-softwareupdater-keys/beta-testbed-softwareupdater.publickey \
  /root/beta-testbed-softwareupdater-keys/beta-testbed-softwareupdater.privatekey \
  $BASE_INSTALLER_DIRECTORY \
  $VERSION

if [ "$?" != "0" ]; then
  echo "Building base installers failed."
  exit 1
fi

echo "Changing base installer symlinks used by seattlegeni."

pushd $BASE_INSTALLER_DIRECTORY

if [ ! -f "seattle_${VERSION}_linux.tgz" ] || [ ! -f "seattle_${VERSION}_mac.tgz" ] || [ ! -f "seattle_${VERSION}_win.zip" ]; then
  echo "The base installers don't appear to have been created."
  exit 1
fi

sudo chown geni seattle_*

sudo -u geni ln -s -f seattle_${VERSION}_linux.tgz seattle_linux.tar.gz
sudo -u geni ln -s -f seattle_${VERSION}_mac.tgz seattle_mac.tar.gz
sudo -u geni ln -s -f seattle_${VERSION}_win.zip seattle_windows.zip

popd

echo "New base installers created and installed for seattlegeni."

