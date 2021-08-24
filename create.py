#!/bin/env python3

'''The file creation part, separated, because things are
getting complicated.
'''

#import subprocess
import os
import pathlib


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

if __name__ == '__main__':
    root_dir = '/p/lflood/defazio1/migrate/metadata-tests' #sys.argv[1]
    n = 256 #int(sys.argv[2])
    create_files(root_dir, n)
