'''This script combines 'lfs setstrip' and lfs `setdirstripe`
with mdtest to create trees of files in lustre.
'''

import pathlib
import sys
import subprocess

#TODO assumes that args passed in are already in list form
def create_single_tree(path,
                       setdirstripe_args=None,
                       setstripe_args=None,
                       mdtest_args=None
                       overwrite=False):
    '''Create a directory and set its striping
    and dirstriping, then create a file tree in it using
    mdtest.
    '''
    # if user gives no arguments the arglist should be []
    # however, argument defaults should be immutable (like None)
    arg_lists = [setdirstripe_args, setstripe_args, mdtest_arg]
    for i in range(len(arg_lists)):
         arg_lists[i] = [] if arg_lists[i] is None else arg_lists[i]

    path = pathlib.Path(path)

    if path.exists():
        if not overwrite:
            print(f'ERROR: {str(path)} exits, will not overwrite')
            sys.exit(1)
        else:
            # whatever is at path, which might be a lot
            # so use something like mpifileutils or mdtest
            pass

    # must use lfs setdirsripe at creation time
    subprocess.run(
        ['lfs', 'setdirstripe'] + setdirstripe_args + [path],
        check=True
    )

    if setstripe_args is not None:
    subprocess.run(
        ['lfs', 'setstripe'] + setstripe_args + [path],
        check=True
    )

    subprocess.run(
        ['srun', 'mdtest']
    )


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--setstripe-args',
        help='argument string to pass directly to lfs setstripe'
    )
    parser.add_argument(
        '--setdirstripe-args',
        help='argument string to pass directly to lfs setdirstripe'
    )
    parser.add_argument(
        '--mdtest-args',
        help='argument string to pass directly to lfs mdtest'
    )
