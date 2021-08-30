'''
srun -N2 -n4 -p pgarter -l dsync /p/lflood/defazio1/migrate/metadata-tests-unstriped/8_32_4096 /p/lflood/defazio1/migrate/dsync/MDT3

Create various directory structures, then dsync them to make new directory
structures, do this recusively. See how it scales on big, flat, directories.


Leaf: empty directory of file
      params: directory/file, size

Node: contains leaves or other nodes


Ideas for basic strutures (leaves):
big/small flat directory with files of fixed size
big/small flat directory with files of varying sizes
big/small flat directory with lots of empty directories

params for leaves: total number of files/empty dirs
                   files/empty dir ratio
                   random generator for files sizes

Ideas for nested structures (nodes):
height in tree (leaves have a height of 1 as they are directories with stuff in
them, all all that stuff has height zero)


Need to create dirs with specific dirstripe to stuff goes to correct MDT
also need to stripe correctly, so object go to correct OSTs
'''


def _default_name_func(n):
    '''Consecutive numbers in [0,n-1] as string and zero padded up to
    the length of str(n-1)
    '''
    max_number_length = len(str(n-1))
    return (str(x).zfill(max_number_length) in range(n))

def _default_size_func(n):
    '''Return 0 n times.'''
    return (0 for _ in range(n))

def create_n_files(n, directory, size_func=None, name_func=None,
                   fraction_files=1.0):
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

    num_files = (n * fraction_files).round()
    num_dirs = (n * (1.0 - fraction_files)).round()
    #round_error = n - (num_files + num_dirs)

    # check if directory exists, error, if not, create it, record if it was created
    d = pathlib.Path(directory)
    d.mkdir()

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
            with open((d / name), 'w') as f:
                f.write(os.urandom(n))


# TODO need to specify -N and -n
def create_tree_with_n_copies(n, tree_path, dir_to_copy):
    '''Create a dir that contains n copies of an existing dir'''
    d = pathlib.Path(tree_path)
    d.mkdir()

    # use dsync to create n copies
    for name in _default_name_func(n):
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
            ]
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
        root = str(len(copies_at_depth) - i)
        create_tree_with_n_copies(n, root, dir_to_copy)
        dir_to_copy = root

    return root
