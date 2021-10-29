# Testing plan for lfs-migrate performace testing
It was noticed while trying to use lfs migrate for meta-data
migration, that lfs-migrate has poor performance.
Even when using many threads, sustained performance was around
400 items/second, which is to slow to be practical for migrations
of large numbers of files and directories.

This testing plan is for performing a new test to see if the above results
are in fact the limit, or near the limit of lfs-migrate's performance,
or if the original tests were flawed in some way.
Some possible ways the tests were flawed are:
- the setup was wrong in some way and the results are not from the intended tests
- the results were interpreted incorrectly
- there are tweaks and tricks needed to make lfs-migate fast that were not used

This plan is intended to be reviewed by people at llnl and also whamcloud
to help avoid repeating any mistakes that may have been in the first round of
tests, and to potentially get ideas for features that should be added to
better evaluate the performace of lfs-migrate.

## Description of previous tests

## Results of previous tests
