#!/bin/env python3

# TODO pass in ouptut dir

#### shared functions

#### process 0 only

# create the dir where all the results go

'''wrap a single slurm process doing lfs-migrate.
Process 0 logs meta-data for the entire run.
All process do a 'lfs migrate <flags and args>' call
and record the results.

This is meant to be run via srun
srun <srun flags and args> python3 multi_lfs_migrate <flag and args>

The prerequistes are:
The log directory needs to exist.
The files directory and subdirectories need to exist.
There needs to be a subdirectory for every slurm process,
for example, if there are 16 proccesses, the directories
<files directory>[0-15] must exist.
'''

import argparse
import os
import pathlib
import sys

import yaml

def log_run_data(args):
    '''Gather the metadata for the whole run
    and write it to a file as yaml.
    '''
    # log the meta_data fo the whole run

    # capture a bunch of slurm environment variables
    slurm_params = [
        'SLURM_NPROCS',
        'SLURM_NNODES',
        'SLURM_CLUSTER_NAME',
        'SLURM_JOB_ID',
        'SLURM_JOB_PARTITION',
    ]

    slurm_data = {param: os.environ.get(param) for param in slurm_params}

    meta_data = {
        'slurm_data': slurm_data,
        #'srun-command': srun_command,
        'argv': sys.argv,
        #'num-procs': int(args['num_procs']),
        #'num-nodes': int(args['num_nodes']),
        'total-files': None,
        'num-dirs': None,
        'mdt-config-initial': None,
        #'mdt-config-final': args['migrate_index'],
        'filesystem': None,
        'timestamp': str(datetime.datetime.now())
    }

    log_dir = pathlib.Path(args['output_directory'])
    with open(log_dir / 'meta-data.yaml', 'w+') as f:
        yaml.safe_dump(meta_data, f)


def lfs_migrate(args):
    '''Do a run for a sin gle srun process.
    Get the start time, do the lfs migrate,
    get the end time, write the results.
    '''

    spid = str(os.environ.get('SLURM_PROCID'))
     # for the case that slurm is not being used
    if spid is None:
        spid = 0

    files_root_dir = pathlib.Path(args['files_dir'])
    logs_root_dir = pathlib.Path(args['logs_dir'])
    files_sub_dir = str(files_root_dir / str(spid))
    results_file = str(logs_root_dir / str(spid))

    # construct the lfs-migrate command
    cmd = ['lfs', 'migrate']
    if args['migrate_index']:
        cmd += ['-m', args['migrate_index']]
    if args['mdt_count']:
        cmd += ['-c', args['mdt_count']]
    cmd.append(files_sub_dir)

    start_time = datetime.datetime.now()

    # run the lfs-migrate command and capture its output
    s = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    end_time = datetime.datetime.now()

    with open(results_file, 'w') as f:
        yaml.safe_dump(
            {
                'args': sys.argv,
                'start-time': start_time,
                'end-time': end_time,
                'stdout': s.stdout.decode(),
                'stderr': s.stderr.decode(),
            },
            f
        )


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--migrate-index',
        help='passed to lfs migrate',
    )
    parser.add_argument(
        '-c',
        '--mdt-count',
        help='passed to lfs migrate',
    )
    parser.add_argument(
        '-f',
        '--files-dir',
        required=True,
        help='the files directory'
    )
    parser.add_argument(
        '-l',
        '--logs-dir',
        required=True,
        help='the directory where output files go, needs to already exist',
    )
    parser.add_argument(
        '--dryrun',
        action='store_true',
        help='print out the srun command but don\'t run it'
    )
    parser.add_argument(
        '-o',
        '--objects',
        help='q'
    )
    return parser


def main():
    args = vars(make_parser().parse_args())
    procid = os.environ.get('SLURM_PROCID')
    if procid == 0:
        log_run_data(args)
    lfs_migrate(args)

if __name__ == '__main__':
    main()
