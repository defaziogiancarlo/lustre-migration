#!/bin/env python3

'''The file creation part, separated, because things are
getting complicated.
'''

#import subprocess
import argparse
import os
import pathlib
import subprocess

spid = str(os.environ.get('SLURM_PROCID'))

# def get_hostname():
#     '''For some reason root does have HOSTNAME in env,
#     so you the hostname utility instead.
#     '''
#     return subprocess.run(
#         ['hostname'],
#         check=True,
#         stdout=subprocess.PIPE,
#     ).stdout.decode().strip()


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


def _create_node_proc_files_srun_single(root_dir, n):
    '''Create files with the structure:
    topdir->nodedir->procdir->files.
    A process first creates the topedir and nodedirs,
    then a bunch of processes fill in the procdirs and
    files.
    The root_dir will be made.
    '''

    # create the root dir
    # (all processes will attempt this)
    #root_dir = pathlib.Path(root_dir)
    #root_dir.mkdir(exist_ok=True)

    # now create the node dirs
    # (all processes on a particular node will attemp this)
    node_num = str(os.environ['SLURM_NODEID'])
    node_dir = root_dir / node_num
    node_dir.mkdir(exist_ok=True)

    # now create the dir for this process
    local_id = str(os.environ['SLURM_LOCALID'])
    proc_dir = node_dir / local_id
    proc_dir.mkdir()

    # now the files with the localid dir
    n = int(n)
    number_length = len(str(n-1))
    for i in range(n):
        filename = str(i).zfill(number_length)
        (proc_dir / filename).touch()


def create_node_proc_files(num_nodes, num_procs, root_dir, num_files_per_dir):
    '''Create files is a
    topdir -> node_dir -> proc_dir -> files tree
    top_dir should not exist
    uses srun to run a bunch of _create_node_proc_files_srun_single_proc
    instances to do most of the work
    '''

    # create the root dir
    # (or all processes will attempt this)
    root_dir = pathlib.Path(root_dir)
    # if it already exists, don't mess with it
    if root_dir.is_dir():
        return
    root_dir.mkdir()

    # put a meta-data.yaml file in the dir
    meta_data = {
        'files_per_dir': int(num_files_per_dir),
        'num_nodes': int(num_nodes),
        'num_procs': int(num_procs),
        'nexted_by_node': True,
        'total_files': int(num_procs) * int(num_files_per_dir),
    }

    with open(root_dir / 'meta-data.yaml') as f:
        yaml.safe_dump(meta_data, f)

    srun_command = (
        [
            # the srun part
            'srun',
            f'-N{num_nodes}',
            f'-n{num_procs}',
            '-p', 'pgarter',
            '-l',
        ]
        +
        # the single process command part
        [
            pathlib.Path(__file__).resolve(),
            '--create-node-proc-files-srun-single',
            '--root-dir', root_dir,
            '--files-per-dir', num_files_per_dir,
        ]
    )
    subprocess.run(srun_command)


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--create-node-proc-files',
        action='store_true',
        help='create files',
    )
    parser.add_argument(
        '--create-node-proc-files-srun-single',
        action='store_true',
        help='create files',
    )
    parser.add_argument(
        '--root-dir',
        help='create files',
    )
    parser.add_argument(
        '--files-per-dir',
        help='create files'
    )
    parser.add_argument(
        '--num-nodes',
        help='number of nodes, passed to srun',
    )
    parser.add_argument(
        '--num-procs',
        help='number of processes, passed to srun'
    )
    return parser

def main(args=None):
    if args is None:
        parser = make_parser()
        args = vars(parser.parse_args())

    # called directly from command line
    if args['create_node_proc_files']:
        create_node_proc_files(
            args['num_nodes'],
            args['num_procs'],
            args['root_dir'],
            args['files_per_dir'],
        )

    # called inderectly by create_node_proc_files using srun
    if args['create_node_proc_files_srun_single']:
        _create_node_proc_files_srun_single(
            args['root_dir'],
            args['files_per_dir'],
        )

if __name__ == '__main__':
    # root_dir = '/p/lflood/defazio1/migrate/metadata-tests/256_512' #sys.argv[1]
    # n = 512 #int(sys.argv[2])
    # create_files(root_dir, n)
    main()
