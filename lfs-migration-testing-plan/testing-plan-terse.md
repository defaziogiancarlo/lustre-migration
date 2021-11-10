# Testing plan for lfs-migrate performace testing
While trying to use lfs-migrate for meta-data
migration, we found that lfs-migrate has poor performance.
Even when using many threads, sustained performance was around
400 items/second, which is too slow to be practical for migrations
of large numbers of files and directories.

This testing plan is for performing a new test to see if the above results
are in fact the limit, or near the limit of lfs-migrate's performance,
or if the original tests were flawed in some way.

This plan is intended to be reviewed by people at llnl and also whamcloud
to help avoid repeating any mistakes that may have been in the first round of
tests, and to potentially get ideas for features that should be added to
better evaluate the performance of lfs-migrate.

## Description of previous tests

### Overview
The previous tests first created a directory structure, then used many
processes, each an instance of `lfs`, called on some subdirectory in the
directory structure. Each thread had essentially the same job, because the
contents of each subdirectory were the same, and they were all migrating
metadata from and to the same MDTs.
The previous tests only did meta-data. Object data tests were not done.

#### directory setup
The directories that were to be migrated were set up as trees
with a structure
root (-> node)* -> leaf
The root is a single directory that branches to n\_0 nodes.
Each node is directory that contains either
n\_x (branching factor at depth of x) nodes, or k leaves.
The branching factor is the same for all nodes at a given depth.
At the bottom are the leaves. In this case there are k leaves, which are
either empty files or empty directories, or some combination.

For a test run, a height was picked, and each node at that height was assigned
a process running lfs-migrate.

#### Doing the migration
The process to actually run the commands is a bit convoluted.

A python script is run which creates the command\_file that is just a call
to a another python script. In fact, it's even worse than that, it's to the same
script but with different arguments.

Then that initial python script runs the `srun` command with the appropriate
flags and the command_\file as an input.

Many instances of the command\_file are run by `srun` and each grabs the start
time, run its `lfs-migrate` command, gets the output of `lfs-migrate`, which
should be nothing if all went well, and then grabs the end time.
Then, it writes all of this data to a file, so there is a file per-process
per-run.

The initial script also creates a meta-data file with data for the whole run.

The command\_file, the meta-data file, and the output files for each srun
process are all put into a time-stamped directory.

#### Interpreting the results
Another script is used to process and aggregate the data in the per-process
files and give a summary of the whole run. Most importantly, it calculates
items/second. The results are output as a csv.


## Results of previous tests
The results are in a spreadsheet.
The main result was that performance does go up with more
processes and nodes, but sub-linearly, and levels off around
400 items/sec sustained performance.
Performance levels off at 32 total processes, and doesn't really improve much
up to the max of 256 tested.


## Plan for second test
For the most part I intend to repeat the first test, but in
a more thorough and systematic way.
The overall plan is still to make a tree, then migrate it.
My intent is to split it into 3 phases:
- create the trees
- migrate the tree
- analyze the data generated during the migration

### create the trees
The tree can be created using `mdtest`.
`mdtest` has most of the options I care about, and the exact
creation command can be saved in the meta-data of the test to make it easy
to repeat tests.

The only major shortcoming with `mdtest` is that it's difficult to set
different striping and directory striping to the trees it creates.
This can be overcome by pre-creating directories,
setting their striping and directory striping, and then having `mdtest`
create trees within these directories so that each tree inherits
these setting from its respective parent directory.

### migrate the tree
The migration is done in parallel by many processes, each running
`lfs-migrate` on one of the directories mentioned above.
This allows parallelism on the client side, and also the ability to do
various (from,to) combinations of MDTs and OSTs.

Data needs to be collected during the run. Process 0 will write the data for
the whole run, and each process will write its own performance data.
This will generate 1 file per processes, and 1 more for the run-wide data.

#### data to collect per test run
- start time
- end time
- the lfs-migrate command
- where the output data is written
- total items migrated
- the mdtest command and the striping/dirstriping
- slurm info, especially the jobid

#### data to collect per process
- what kind of items are migrated (files/directories)
- migration start and stop time
- source MDTs
- destination MDTs
- the lfs-migrate command

Many tests can be run, with varying parameters

#### parameters to vary
- the number of processes
- the number of nodes used
- the kind of items that are migrated
- how many items per process are migrated
