'''One file to create files,
do the lfs-migrate runs,
and consolidate the output,
and maybe make a graph? probably not.
'''

import pathlib

import analyze
import create
import meta_data

def make_combos():
    combos = []
    for num_nodes in [1, 2, 4, 8, 16]:
        for num_procs in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
            for num_files in [1, 8, 64, 512, 4096]:
                if num_procs < num_nodes:
                    continue
                combos.append((num_nodes, num_procs, num_files))



root_root_dir = pathlib.Path(
    '/p/lflood/defazio1/migrate/metadata-tests'
)

def do_single_run(num_nodes, num_procs, num_files):

    # create the files

    # create the dir name
    params = [num_nodes, num_procs, num_files]
    name = '_'.join([str(p) for p in params])
    root_dir = root_root_dir / name

    # creat the dirs and files (and meta_data!)
    create.create_node_proc_files(num_nodes, num_procs, root_dir, num_files)

    # do the run to put files on 2 nodes
    subprocess.run(
        [
            '/g/g0/defazio1/non-jira-projects/migration/meta_data.py',
            '--setup',
            '--migrate-index', '2,3',
            '--num-procs', str(num_procs),
            '--num_nodes', str(num_nodes),
            '--files-dir', root_dir,
            '--nested-by-node',
        ]
    )

    # do the run to put files on 4 nodes
    subprocess.run(
        [
            '/g/g0/defazio1/non-jira-projects/migration/meta_data.py',
            '--setup',
            '--migrate-index', '0,1,2,3',
            '--num-procs', str(num_procs),
            '--num_nodes', str(num_nodes),
            '--files-dir', root_dir,
            '--nested-by-node',
        ]
    )


def do_multilple_runs():
    '''do a bunch of runs'''
    combos = make_combos()
    for combo in combos:
        do_single_run(*combo)
