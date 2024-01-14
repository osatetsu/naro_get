#! /bin/sh

WGET=/d/tool/wget-1.21.4-win64/wget.exe
REMOTE_HOST=https://ncode.syosetu.com/
DOWNLOAD_DIR=download
WAIT_TIME_SEC=1

if [ -z "$1" ]
then
	echo "Usage: $0 <n_code>"
	exit 1
fi

###"$WGET" --directory-prefix="$DOWNLOAD_DIR" --mirror -nH --no-parent --relative --accept '*.html' --wait="$WAIT_TIME_SEC" --random-wait --verbose "$REMOTE_HOST$1/"
"$WGET" --directory-prefix="$DOWNLOAD_DIR" --mirror -nH --no-parent --wait="$WAIT_TIME_SEC" --random-wait --verbose "$REMOTE_HOST$1/"
