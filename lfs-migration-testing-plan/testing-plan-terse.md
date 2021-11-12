# lfs-migrate Performance Testing
While trying to use `lfs-migrate` for meta-data
migration, we found that the `lfs-migrate` does not scale well.
Even when using many threads, sustained performance was around
400 items/second, which is too slow to be practical for migrations
of large numbers of files and directories.

This testing plan is for performing additional tests to see if the
above results are in fact the limit, or near the limit of `lfs-migrate`'s
performance.

## Overview
The performance to be measured is the rate at which items
(files and directories) can be migrated. These items will be in
a tree (or trees) and migrated by many processes running
`lfs-migrate` in parallel.

The 3 basic parts of the test are:
- create the trees
- migrate the trees
- analyze the data generated during the migration

### Create the Trees
A single tree can be created using `mdtest`.
`mdtest` has the ability to make trees of files and directories,
and can parameterize those trees in most of the ways neccesary for this test.
The `mdtest` command can be saved in the meta-data of the test to make it easy
to recreate the trees when repeating the test.

The only major shortcoming with `mdtest` is that it doesn't set
the striping and directory striping of the trees it creates.
This can be overcome by pre-creating directories,
setting their striping and directory striping, and then having `mdtest`
create trees within these directories so that each tree inherits
these setting from its respective parent directory.

The command to create the trees needs to be saved. This includes
both the `mdtest` command per directory, and also the command to make
the directories and set their striping and directory striping.
Also, `mdtest` will be run with `srun`, so really the whole `srun`
command needs to be saved.

### Migrate the Trees
The migration is done in parallel by many processes, each running
`lfs-migrate` on one of the directories that contains a tree created
by `mdtest`. The many processes are created and spread across multiple
client nodes using `srun`.

Data needs to be collected during the run. Process 0 will write the data for
the whole run, and each process will write its own performance data.
This will generate 1 file per processes, and 1 more for the run-wide data.
Some of the collected data could be inferred from other data (or from the slurm
database) but it's easier to just grab it anyays to simplify post-processing.

#### Data to Collect Per Run
- total items migrated
- the mdtest command and the striping/dirstriping commands
- slurm jobid
- the srun command the does the migration
- metadata/object data/both

#### Data to Collect Per Process
- start time (of lfs-migrate)
- end time (of lfs-migrate)
- source MDTs/OSTs
- destination MDTs/OSTs
- the lfs-migrate command (which contains some of the above info)

#### Parameters to Vary between Runs
- the number of processes (1-256)
- the number of nodes (1-16)
- the kind of items that are migrated (files/directories/some of each)
- how many items per process are migrated (1-4096(at least))

### Data Analysis
The data recorded for each run will all go into a single directory.
A script will read the meta-data and per-process perfomance data, and
calculate the rate at which items are migrated as well
as the data rate.


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
