#!/bin/sh

DATA_FOLDER="../data"

MUSIC_FILE="$DATA_FOLDER/$1"

DEST_FILE="/usr/share/games/extremetuxracer/music/race1-jt.it"

echo "Moving [$MUSIC_FILE] to [$DEST_FILE]"

sudo cp "$MUSIC_FILE" "$DEST_FILE"
