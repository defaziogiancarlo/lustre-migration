'''
Create directory trees.

These trees have all their contents stored in the leaves.
The leaves are themselves directories that contain only
files and empty directories.

All the leaves are identical and are at the same depth.

The structure of the trees is a root directory which branches
to N_0 directories, which are leaves or nodes. If they are nodes
they branch to N_1 directories, which again can be either leaves or
nodes. This branching factor is the same for all nodes at a given depth.

The depth and branching factor at each depth can be set for the tree.
Also, the number of items in each leaf, the ratio of empty directories to files
in each leaf, and a function to set the file sizes can be specified.
'''

import os
import pathlib
import random
import subprocess

import yaml

def _default_name_func(n):
    '''Consecutive numbers in [0,n-1] as string and zero padded up to
    the length of str(n-1)
    '''
    max_number_length = len(str(n-1))
    return (str(x).zfill(max_number_length) for x in range(n))

def _default_size_func(n):
    '''Return 0 n times.'''
    return (0 for _ in range(n))

def random_0_to_64M(n):
    MiB = 2**20
    return (random.randrange(0, 64 * MiB, MiB) for _ in range(n))

def create_n_files(n, directory, size_func=None, name_func=None,
                   fraction_files=1.0, stripe=None, dirstripe=None):
    '''Create n files in directory,
    The directory will be created if it doesn't exist.
    By default, empty files will be created.
    If make_dirs is True, empty directories will be made.
    If make_dires is False, and size_func is not None,
    size_func will be used to calculate n values that
    will be used as the file sizes. The files will contain random data.
    '''

    if fraction_files > 1.0 or fraction_files < 0.0:
        print('ERROR: ratio must be in [0.0, 1.0]', file=sys.stderr)
        sys.exit(1)

    num_files = round(n * fraction_files)
    num_dirs = round(n * (1.0 - fraction_files))
    #round_error = n - (num_files + num_dirs)

    # check if directory exists, error, if not, create it, record if it was created
    d = pathlib.Path(directory)
    d.mkdir()

    # now set strip and distripe attributes of directory
    # TODO should I just precreate some dirs, and set their
    # stuff, then make subdirs, so that I don't need to be root?


    # generate names
    name_func = name_func if name_func is not None else _default_name_func
    size_func = size_func if size_func is not None else _default_size_func

    for name in name_func(num_dirs):
        (d / ('dir_' + name)).mkdir()

    # TODO could optimize further, if you're using the _default_size_func
    # no need to check for 0, or even generate them, just do the touch()
    for name, size in zip(name_func(num_files), size_func(num_files)):
        if size == 0:
            (d / name).touch()
        else:
            with open((d / name), 'wb') as f:
                f.write(os.urandom(size))


def create_tree_with_n_copies(n, tree_path, dir_to_copy, num_nodes=8, num_procs=64):
    '''Create a dir that contains n copies of an existing dir'''
    d = pathlib.Path(tree_path)
    subprocess.run(
        [f'pdsh -w ecatalyst205 mkdir {str(tree_path)}'],
        shell=True,
        check=True,
    )
    # d.mkdir()

    # use dsync to create n copies
    for name in _default_name_func(n):
        print(name)
        subprocess.run(
            [
                'srun',
                '-p', 'pgarter',
                f'-N{num_nodes}',
                f'-n{num_procs}',
                '-l',
                'dsync',
                dir_to_copy,
                (d / name),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

def create_tree_copies(copies_at_depth, tree_path, dir_to_copy):
    '''Create a tree that has dir_to_copy as its leaves.
    copies_at_depth will, starting at the max depth (last element)
    create copies_at_depth[-1] copies of dir_to_copy, then
    copies_at_depth[-2] of that result, and so for the the top of the tree.
    The result is a tree with only directories for its nodes, and
    product(copies_at_depth) copies of dir_to_copy as its leaves.
    '''

    # create the names of the directories

    for i,n in enumerate(reversed(copies_at_depth)):
        root = pathlib.Path(tree_path) / str(len(copies_at_depth) - i)
        create_tree_with_n_copies(n, root, dir_to_copy)
        dir_to_copy = root

    return root
