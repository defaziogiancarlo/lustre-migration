# Testing plan for lfs-migrate performace testing
It was noticed while trying to use lfs-migrate for meta-data
migration, that lfs-migrate has poor performance.
Even when using many threads, sustained performance was around
400 items/second, which is too slow to be practical for migrations
of large numbers of files and directories.

This testing plan is for performing a new test to see if the above results
are in fact the limit, or near the limit of lfs-migrate's performance,
or if the original tests were flawed in some way.
Some possible ways the tests were flawed are:
- the setup was wrong in some way and the results are not from the intended setup
- the results were interpreted incorrectly
- there are tweaks and tricks needed to make lfs-migate fast that were not used

This plan is intended to be reviewed by people at llnl and also whamcloud
to help avoid repeating any mistakes that may have been in the first round of
tests, and to potentially get ideas for features that should be added to
better evaluate the performace of lfs-migrate.

## Description of previous tests

### overview
The previous tests first created a directory structure, then used many
proccesses, each an instance of `lfs`, called on some subdirectory in the
directory structure. Each thread had esentially the same job, because the
contents of each subdirectory were the same, and they were all migrating
metadata from and to the same MDTs.

### details
#### directory setup
The directories that were to be moved where set up as trees
with a structure
root (-> node)* -> leaf
The root is a single directory that branches to n\_0 nodes.
Each node is directory that contains either n\_x nodes, or k leaves.
The branching factor is the same for all nodes at a given depth,
and the subscript represents the depth of the node.
At the bottom are the leaves. In this case there are k leaves, which are
either empty files or empty directories, in the parent node.

For a test run, a height was picked, and each node at that height was assigned
a proccess running lfs-migrate.

#### Running the migrate
The process to actually run the commands is a bit convoluted.

A python script is run which creates the command\_file that is just a call to a python script

Then that initial python script runs the `srun` command with the appropriate flags
and the command_\file as an input.

Many instances of the command\_file are run by `srun` and each grabs the start
time, run it's `lfs-migrate` command, gets the output of `lfs-migrate`, which
should be nothing if all went well, and then grabs the end time.
Then, it writes all of this data to a file, so there is a file per-preocess
per-run.

The initial script also creates a meta-data file with data for the whole run.

The command\_file, the meta-data file, and the output files for each srun
process are all put into a time-stamped directory.

#### Intrepreting the results
Another script is used to process and aggregate the data in the per-process
files and give a summary of the whole run.


## Results of previous tests
The results are in a spreadsheet.
The main result was that perfomance does go up with more
processes and nodes, but sub-linearly, and ends up around
400 items/sec sustained performance.


## Plan for second test
For the most part I intend to repeat the first test, but in
a more thorough and systematic way.

### questions about possible changes

- Should I be using slurm to do a bunch of simultious `lfs-migrate`s
all on the same diretory tree?
- Should I be migrating different arrangement of files/directories
to better reflect real migration workloads
- are there lustre,lnet,etc. settings that should be changed to help
perfomance
- did I have the preferred zfs/jbod setting on garter when I did the tests?
(I believe the answer is no) This my help a little bit?
- Are there other tools I should be using? similar the the one in mpifileutils?


- Will lfs-migrate end up limited by data operations and not meta-data
operations for real workloads anyways?

### data to collect

#### per test run
- start time
- end time
- the srun command
- where the output data is written
- total items migrated

#### per process
- number of items migrated for each process
- what kind of items are migrated
- migration start and stop time
- source MDTs
- destination MDTs
- the lfs-migrate command


### parameters to vary

- the number of processes
- the number of client nodes used
- the number of processes per client node
- what kinda of items are migrated
- how many items per proces are migrated
