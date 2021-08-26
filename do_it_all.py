'''One file to create files,
do the lfs-migrate runs,
and consolidate the output,
and maybe make a graph? probably not.
'''

import pathlib
import subprocess

import analyze
import create
import meta_data

def make_combos(num_nodes_list=None, num_procs_list=None, num_files_list=None):
    if num_nodes_list is None:
        num_nodes_list = [1, 2, 4, 8, 16]
    if num_procs_list is None:
        num_procs_list = [1, 2, 4, 8, 16]
    if num_files_list is None:
        num_files_list = [1, 8, 64, 512, 4096, 65536]

    combos = []
    for num_nodes in num_nodes_list:
        for num_procs in num_procs_list:
            for num_files in num_files_list:
                if num_procs < num_nodes:
                    continue
                combos.append((num_nodes, num_procs, num_files))
    return combos


root_root_dir = pathlib.Path(
    '/p/lflood/defazio1/migrate/metadata-tests-unstriped'
)

def do_single_run(num_nodes, num_procs, num_files, directories,
                  mdt_initial, mdt_final):

    # create the files

    # create the dir name
    params = [num_nodes, num_procs, num_files]
    name = '_'.join([str(p) for p in params])
    if directories:
        name = 'd' + name
    root_dir = root_root_dir / name

    # creat the dirs and files (and meta_data!)
    create.create_node_proc_files(
        str(num_nodes),
        str(num_procs),
        root_dir,
        str(num_files),
        directories=directories,
    )

    # do the run to put files on 2 nodes
    subprocess.run(
        [
            '/g/g0/defazio1/non-jira-projects/migration/meta_data.py',
            '--setup',
            '--migrate-index', str(mdt_initial),
            '--num-procs', str(num_procs),
            '--num-nodes', str(num_nodes),
            '--files-dir', root_dir,
            '--nested-by-node',
        ]
    )

    # do the run to put files on 4 nodes
    subprocess.run(
        [
            '/g/g0/defazio1/non-jira-projects/migration/meta_data.py',
            '--setup',
            '--migrate-index', str(mdt_final),
            '--num-procs', str(num_procs),
            '--num-nodes', str(num_nodes),
            '--files-dir', root_dir,
            '--nested-by-node',
        ]
    )


def do_multilple_runs(directories, mdt_initial, mdt_final):
    '''do a bunch of runs'''
    combos = make_combos()
    for combo in combos:
        do_single_run(*combo, directories, mdt_initial, mdt_final)

if __name__ == '__main__':
    do_multilple_runs(False, 2, 3)
