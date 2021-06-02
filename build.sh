#!/usr/bin/env sh

source bin/activate

CWD=$(pwd)
ZIP_NAME="$CWD/JakeSky.zip"

rm -f "$ZIP_NAME"
zip -9 "$ZIP_NAME"
pushd "lib/python3.8/site-packages"
zip -r9 "$ZIP_NAME" *
popd
zip -g "$ZIP_NAME" jakesky.py
