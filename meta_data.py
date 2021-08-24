#!/bin/env python3

'''The meta data tests

The basic idea is to create a bunch of files,
then move them to an MDT, or set of MDTs, then maybe move them again.

The goal is to use srun, to scale up to muliple nodes.

That means that each process needs to write all of it's run data somewhere
and then all that data can be consolidated.

Important data for each run:
start time, stop time, total files, how files are arranged
initial MDT configuration, final MDT configuration

Each process should know what directory it does, how many files
are in the directory, it's actual start and end times, where to write
its data.

Then consolidate the data.

This file sets up the runs, then is called again, and does the individual runs
it should probably be split into 2 files, and then a third for data aggregation.
'''

import argparse
import copy
import datetime
import os
import pathlib
import pprint
import subprocess
import sys

import yaml

def get_hostname():
    '''For some reason root does have HOSTNAME in env,
    so use the hostname utility instead.
    '''
    return subprocess.run(
        ['hostname'],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode().strip()

def de_tuple_list(x):
    '''Take a list of tuples, or other things
    that could be turn into lists,
    and flatten it one level.
    '''
    acc = []
    for i in x:
        acc += list(i)
    return acc

def timestamp():
    '''Make a timestamp that can be used as a file name.'''
    return str(datetime.datetime.now()).replace(' ', '_').replace(':', '')

# where all the logs go for the tests
root_log_dir = pathlib.Path(
    '/g/g0/defazio1/non-jira-projects/migration/data'
)

# where the actual files go for the tests (in lustre)
#if 'catalyst' in hostname():
root_files_dir = pathlib.Path(
    '/p/lflood/defazio1/migrate/metadata-tests'
)
#if 'opal' in hostname():


# some of this code is meant to be run by srun,
# and the proccess id may be used to determine what
# each process does
spid = str(os.environ.get('SLURM_PROCID'))

def make_run_data(spid, start, end):
    data = {
        'procid': spid,
        'start': start,
        'end': end,
    }

def create_files(root_path):
    '''Create the files for your directory'''
    pass

def migrate_files(root_path):
    '''migrate the files for your directory.'''
    pass

#def create_srun_command()


def make_command_migrate(args):
    '''Do the actual migrate command.
    '''
    cmd = ['lfs', 'migrate']
    if args['migrate_index']:
        cmd += ['-m', args['migrate_index']]
    if args['mdt_count']:
        cmd += ['-c', args['mdt_count']]
    cmd.append(files_dir)

    return cmd




def do_run(args):
    '''Do a run for a single sun process.
    Get the start time, do the lfs migrate,
    get the end time, write the results.
    '''
    start_time = datetime.datetime.now()

    spid = str(os.environ.get('SLURM_PROCID'))
    if spid is None:
        spid = 0

    files_root_dir = pathlib.Path(args['files_dir'])
    logs_root_dir = pathlib.Path(args['logs_dir'])
    files_dir = str(files_root_dir / str(spid))
    logs_dir = str(logs_root_dir / str(spid))

    #print('DOING RUN')

    cmd = ['lfs', 'migrate']
    if args['migrate_index']:
        cmd += ['-m', args['migrate_index']]
    if args['mdt_count']:
        cmd += ['-c', args['mdt_count']]
    cmd.append(str(files_dir))

    # TODO capture output and shove it into the log file?
    s = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    #print('LOGGING RUN')

    end_time = datetime.datetime.now()

    with open(logs_dir, 'w') as f:
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

# def do_run(args):
#     print('RUNNING')
#     with open('/g/g0/defazio1/stuffs/' + str(spid), 'w+') as f:
#         f.write(str(spid))

def make_srun_command(num_nodes, num_procs, command_path):
    '''need to eventually deal with what
    machines you're using.
    catalyst to garter for now
    '''

    hostname = get_hostname()
    if 'catalyst' in hostname:
        batch = 'pgarter'
    if 'opal' in hostname:
        batch = 'pbatch'

    cmd = [
        'srun',
        '-p', batch,
        f'-N{num_nodes}',
        f'-n{num_procs}',
        '--time', '05:59:00',
        '-l',
        str(command_path)
    ]

    return cmd

def make_command(files_dir, logs_dir):

    command = [
        '/g/g0/defazio1/non-jira-projects/migration/meta_data.py',
    ]
    argv = copy.deepcopy(sys.argv)
    argv.remove('meta_data.py')
    if '-s' in argv:
        argv.remove('-s')
    if '--setup' in argv:
        argv.remove('--setup')
    command += argv
    command += ['--logs-dir', str(logs_dir)]

    # if using a preexising files-dir, it will
    # already be in args, so no need to have it twice
    if '--files-dir' not in argv:
        command += ['--files-dir', str(files_dir)]


    return ' '.join(['\'' + c + '\'' for c in command])

def write_command(command, log_dir):
    command_path = log_dir / 'command.sh'
    command_path.touch(mode=0o777, exist_ok=False)
    with open(command_path, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('# autogenerated by meta_data.py\n')
        f.write(command)
        f.write('\n')

def setup_run(args):
    '''Create the directories, write the metadata,
    create the srun file, and run it.
    '''
    ts = timestamp()

    # create the directories
    # for this particular run
    log_dir = root_log_dir / ts
    log_dir.mkdir()

    # if the files dir is premade, don't make a new one
    if args['files_dir'] is not None:
        files_dir = pathlib.Path(args['files_dir'])
        if 'opal' in get_hostname():
            files_dir.mkdir(exist_ok=True)
    else:
        files_dir = root_files_dir / ts
        files_dir.mkdir(exist_ok=False)

    # make the command the all the srun processes will run
    command = make_command(files_dir, log_dir)

    # write the command to a file where srun can find it
    # this will be 'command.sh' in the subdir for this run
    write_command(command, log_dir)

    # create the srun command
    srun_command = make_srun_command(
        args['num_nodes'],
        args['num_procs'],
        str(log_dir / 'command.sh')
    )


    # log the meta_data fo the whole run
    meta_data = {
        'command': command,
        'srun-command': srun_command,
        'argv': sys.argv,
        'num-procs': int(args['num_procs']),
        'num-nodes': int(args['num_nodes']),
        'total-files': None,
        'num-dirs': None,
        'action': 'create' if 'create' in args else 'migrate',
        'mdt-config-initial': None,
        'mdt-config-final': None,
        'filesystem': None,
    }
    with open(log_dir / 'meta-data.yaml', 'w+') as f:
        yaml.safe_dump(meta_data, f)

    print('starting data migration test run:')
    pprint.pprint(meta_data)

    # launch the srun command
    #if not args['dryrun']:
    #    subprocess.run(srun_command)
    print(' '.join(srun_command))

def make_command_migrate(args):
    '''Do the actual migrate command.
    This really means just do an lfs-migrate
    '''
    cmd = ['lfs', 'migrate']
    if args['migrate-index']:
        cmd += ['-m', '\"' + args['migrate-index'] + '\"']
    if args['mdt-count']:
        cmd += ['-c', args['mdt-count']]
    cmd.append(files_dir)

    return cmd

# TODO make it so that you can have multiple processes making files
# in same dir without a race condition
# def create_files(root_dir, n, whole_dir=True, dir_creator=False):
#     '''Create a bunch of files for the purpose of
#     doing migrations on them.
#     This is for a single process doing its own directory
#     '''

#     number_length = len(str(n-1))

#     if whole_dir or dir_creator:
#         my_dir = pathlib.Path(root_dir) / str(spid)
#         my_dir.mkdir()

#     # will be making files in same dir along with other processes
#     if whole_dir == False:

#     for i in range(n):
#         name = str(i).zfill(number_length)
#         # will be making files in same dir along with other processes
#         if whole_dir == False:
#             name =
#         (my_dir / name).touch()

def create_files(root_dir, n):
    '''Create a bunch of files for the purpose of
    doing migrations on them.
    This is for a single process doing its own directory
    '''

    number_length = len(str(n-1))

    my_dir = pathlib.Path(root_dir) / str(spid)
    my_dir.mkdir()


    for i in range(n):
        name = str(i).zfill(number_length)
        (my_dir / name).touch()


# de do run run run de do run run
# def do_run():
#     '''
#     '''
#     pass

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
        '--create',
        help='create files with the given number'
    )
    parser.add_argument(
        '-n',
        '--new-files',
        help='create n new files',
    )
    parser.add_argument(
        '-f',
        '--files-dir',
        help='the files directory'
    )
    parser.add_argument(
        '-l',
        '--logs-dir',
        help='the logs directory'
    )
    parser.add_argument(
        '--num-procs',
        help='number of procs, for srun'
    )
    parser.add_argument(
        '--num-nodes',
        help='number of nodes, for srun'
    )
    parser.add_argument(
        '--dryrun',
        action='store_true',
        help='set everything up, but don\'t actually call srun'
    )
    parser.add_argument(
        '-s',
        '--setup',
        action='store_true',
        help=(
            'set up the directories and write the meta_data. '
            'create and run the srun command.'
        ),
    )

    #parser.add_argument(
    #)

    return parser


def main():
    parser = make_parser()
    args = vars(parser.parse_args())

    if args['setup']:
        setup_run(args)
    else:
        #print('RUN TIME')
        do_run(args)


if __name__ == '__main__':
    main()
