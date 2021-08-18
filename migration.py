#!/bin/env python3

'''A script to test out lfs-migrate on
garter. The plan is to write file with a particualr stripe
pattern, then migrate them.

You need to figure out an apporpriate orginal striping pattern,
and the appropriate final pattern.

The final pattern could be something like the struping default,
with a PFL (progressive file layout) and DoM (data on metadata).

The writing can be done separately, because this experiment assumes that
the writing has already been done, so you don't need to bench mark that part.

You need a script that you can run with srun, and maybe do catalyst
to garter. You'll need to get the process number somehow.
Srun will give you a bunch of environment variables you can get at with
os.environ, the one you want is SLURM_PROCID.

Now, each process needs to do a bunch of lfs migrates to its files,
and potentially, do a migrate to put stuff back to its original striping
so that you can run the test multiple times.

Stuff to record:
(for ost stuff)
How much data you move, how many files, number of processes, number of nodes,
intial striping config and final striping config.


You need to use lfs-migrate and lfs_migrate to do this. So in python, you
need to figure out what the cammands are, start recording all the data about
the run, then issue a bunch of commands (subprocesses?) and then finish
recording data, write out the data to someplace.

Then aggregate the data? Could be done by a separate serial program, just make
sure the data is easy to aggregate.

Need to set the striping using the options for lfs-setstripe and lfs-migrate


Two separate tests: on for data and another for meta-data

For meta data, you could just make a big directory, then migrate it such that
it is only on 2 of the MDTs (the expected starting condition) then do a migrate
to all 4 MDTs (could do this one on garter).
The example in the lfs-migrate man page is

lfs migrate -m 0,2 ./testremote
              Move the inodes contained in directory ./testremote from their current MDT to the MDT with index 0 and 2.

so if you have some directory /p/lflood/defazio1/inode-migrate-test/
you could have either done a set stripe (maybe, not sure if it works for inodes)
of just do a pre-migrate to just 2 of the MDTs

lfs migrate -m 0,2 /p/lflood/defazio1/inode-migrate-test/

Then, to actually test the migrate from 2 to 4
lfs migrate -m 0,1,2,3 /p/lflood/defazio1/inode-migrate-test/


'''

import os

spid = os.environ['SLURM_PROCID']


# write a bunch of files initially
# have files in a bunch of directories
# based on SLURM_PROCID, partition up the files
# processes, and commence migrating


def create_files():
    '''Do the initial file creation.'''
    pass


def get_file_numbers(num_files):
    '''Get the file numbers that this process
    needs to do the migrate for.
    '''

    slurm_procid = os.environ['SLURM_PROCID']
    num_procs = os.environ['SLURM_PROCID']


    return list(range(slurm_procid, num_files, num_procs))

def make_migrate_command(filename):
    '''Make the lfs_migrate command for a single file.'''
    command = [
        'lfs_migrate',
        '--no-rsync', # not sure, but useful to see only how fast lfs_migrate is
        '-R', # restripe to default directory striping, you'll need to set up the default for this to work

    ]
    pass
