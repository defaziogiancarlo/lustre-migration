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




# TODO need to specify -N and -n
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


def _yamlize(text):
    '''preprocess the output from getstripe and getdirstripe so that
    it can be read is as yaml.
    '''
    text = text.decode().split('\n')
    text = [line for line in text if line]
    yaml_lines = []
    for line in text:
        tokens = line.split()
        for i in range(len(tokens) // 2):
            yaml_lines.append(tokens[2*i] + ' ' + tokens[2*i+1])
    return '\n'.join(yaml_lines)

def _load_lustre_yaml(text):
    return yaml.safe_load(_yamlize(text))


def get_meta_data(dirname):
    '''Get the important metadata from a directory'''
    #dsync = '/usr/tce/packages/mpifileutils/mpifileutils-0.11/bin/dsync'
    stripe_data = subprocess.run(
        ['lfs', 'getstripe', '-d', dirname],
        stdout = subprocess.PIPE,
    ).stdout

    dirstripe_data = subprocess.run(
        ['lfs', 'getdirstripe', dirname],
        stdout = subprocess.PIPE,
    ).stdout

    return {
        'stripe': _load_lustre_yaml(stripe_data),
        'dirstripe': _load_lustre_yaml(dirstripe_data)
    }


def get_stripe_and_dirstripe(path):
    '''Get the stripe and dirstripe data for a directory'''
    stripe_data = subprocess.run(
        ['lfs', 'getstripe', '--yaml', '-d', dirname],
        stdout = subprocess.PIPE,
    ).stdout

    dirstripe_data = subprocess.run(
        ['lfs', 'getdirstripe', '--yaml', dirname],
        stdout = subprocess.PIPE,
    ).stdout

    stripe_data = yaml.safe_load(stripe_data)
    dirstripe_data = yaml.safe_load(dirstripe_data)

    return {
        'stripe': stripe_data,
        'dirstripe': dirstripe_data
    }




def build_tree(name, stripe, dirstripe, leaf_params, branching):
    # create the single dir first
    pass

def do_whole_run( ):
    '''
    build up a tree
    specify: leaf dir params and
             branching at each depth
             striping
             dirstriping

    copy the tree:
    specify
        where to copy:
           striping, dirstriping of destination

    for each dsync operation:
       whenever doing a dsync,
       grab the source ans dest strip and dirstrip data
       grab the source tre strucuter params
       grap the dsync output
       put all into files




    '''
    pass

def process_ouptput(text):
    '''Process the output of dsync
    and grab all the data that matters for
    performance.

    important data to capture:

    earliest and latest time

    walk rate
    copy rate
    sync rate

    items
      directories
      files
      links

    '''
    # expect to see [<time_stamp>]
    # but may be 0: [<time_stamp>] with slurm proccess numbers prefixed


    # TODO check for slurm process prefix and remove

    # TODO grab first and last time stamp for total time
    #
    data = {
        'num_items': None,
        'num_directories': None,
        'num_files': None,
        'num_links': None,

        'walk_rate': None,
        'copy_rate': None,
        'sync_rate': None,
        'source_path': None,
        'dest_path': None,

    }

    dsync_timestamp_regex = r'^\[(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\)]'
    time_stamp_format = '%Y-%m-%dT%H:%M:%S'

    # remove any proc numbers and split into lines and strip whitesapce
    text = remove_proc_nums(text)
    text = [line.strip() for line in text.split('\n')]

    for i,line in enumerate(text):
        # get the first timestamp
        if i == 0:
            start_time_stamp = dsync_timestamp_regex.find(line)
            data['start'] = datetime.datetime.strptime(start_time_stamp)
        # get the last time stamp
        if i == len(text) - 1:
            end_time_stamp = dsync_timestamp_regex.find(line)
            data['end'] = datetime.datetime.strptime(end_time_stamp)
        # get the walk rate
        if 'Item rate:' in line:
            pass

        # get the copy rate
        if 'Copy rate:' in line:
            pass
        # get the update rate
