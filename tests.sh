#!/bin/bash

MIGRATE=/p/lflood/defazio1/migrate
SPLIT8=$MIGRATE/32678_split_8

# mkdir $SPLIT8

# for x in {a..h}; do
#     mkdir $SPLIT8/"$x"
#     touch $SPLIT8/"$x"/{a..h}{a..h}{a..h}{a..h} &
# done

for x in {a..h}; do
    lfs migrate -m 1 -c 1 $SPLIT8/"$x" &
done
