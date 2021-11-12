'''This script combines 'lfs setstrip' and lfs `setdirstripe`
with mdtest to create trees of files in lustre.
'''

import argparse
import pathlib
import sys
import subprocess

def split_args(args):
    if isinstance(args, str):
        return args.split()
    return list(args)


#TODO assumes that args passed in are already in list form
def create_single_tree(args):
    '''Create a directory and set its striping
    and dirstriping, then create a file tree in it using
    mdtest.
    '''
    setdirstripe_args = split_args(args.setdirstripe_args)
    setstripe_args = split_args(args.setstripe_args)
    mdtest_args = split_args(args.mdtest_args)

    path = pathlib.Path(args.path)

    if path.exists():
        print(f'ERROR: {str(path)} exits, will not overwrite')
        sys.exit(1)
    #path.mkdir()
    path = str(path)

    # must use lfs setdirsripe at creation time
    subprocess.run(
        ['lfs', 'setdirstripe'] + setdirstripe_args + [path],
        check=True
    )

    if setstripe_args is not []:
        subprocess.run(
            ['lfs', 'setstripe'] + setstripe_args + [path],
            check=True
        )

    subprocess.run(
        ['srun', 'mdtest'] + mdtest_args + ['-d', path],
        check=True
    )


def create_dirs_with_striping(topdir, stripings):
    '''Create a bunch of directories , set the striping and directory striping
    for each.
    '''

    # create topdir

    # --

def make_parser():
    description = (
        'A wrapper around mdtest that allows for creating a directory with '
        'its lustre striping and directory striping set, then filling it with '
        'files using mdtest. '
        'Argument lists should be in quotes. '
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--path',
        help='the path at which the tree is made.'
    )
    # parser.add_argument(
    #     '--setstripe-args',
    #     help='argument string to pass directly to lfs setstripe'
    # )
    parser.add_argument(
        '--setdirstripe-args',
        help='argument string to pass directly to lfs setdirstripe'
    )
    parser.add_argument(
        '--setdirstripe-args',
        help='argument string to pass directly to lfs setdirstripe'
    )
    parser.add_argument(
        '--mdtest-args',
        help='argument string to pass directly to lfs mdtest'
    )
    parser.add_argument(
        '--srun-args',
        help='args to srun',
    )
    return parser

if __name__ == '__main__':
    args = make_parser().parse_args()
    create_single_tree(args)
