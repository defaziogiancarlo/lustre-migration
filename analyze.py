'''Do the data analysis, agregation and, maybe, someday,
the visualization.
'''

import pathlib
import statistics

import yaml

def is_int(x):
    try:
        y = int(x)
        return True
    except:
        return False


def start_end_stats(dirname):
    '''Get all the start and end stats of the
    run logs in the directory.
    '''
    dirname = pathlib.Path(dirname)
    starts = []
    ends = []
    diffs = []
    for path in dirname.glob('*'):
        if not is_int(path.name):
            continue
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            starts.append(data['start-time'])
            ends.append(data['end-time'])
            diffs.append(
                (data['end-time'] - data['start-time']).total_seconds()
            )
            inv_diffs = [1/x for x in diffs]

    # something went wrong , got no data
    if len(diffs) == 0:
        print(f'no data for {dirname.name}')
        raise Exception

    results = {
        'earliest-start-time': min(starts),
        'latest-end-time': max(ends),
        'min-inv-time': min(inv_diffs),
        'max-inv-time': max(inv_diffs),
        # 'average-time': statistics.mean(diffs),
        # 'median-time': statistics.median(diffs),
        # 'variance-time': statistics.variance(diffs),
        # 'inv-variance-time': statistics.variance([1/x for x in diffs])
        'average-inv-time': statistics.mean(inv_diffs),
        'median-inv-time': statistics.median(inv_diffs),
        'stdev-inv-time': statistics.stdev(inv_diffs) if len(inv_diffs) >= 2 else 0,

    }
    results['earliest-to-latest'] = (
        (
            results['latest-end-time'] -
            results['earliest-start-time']
        ).total_seconds()
    )
    return results

def update_meta_data_results(dirname):
    '''update the meta-data.yaml file
    by added the results if they aren't already there.
    '''
    dirname = pathlib.Path(dirname)
    meta_data_path = dirname / 'meta-data.yaml'
    # first get the meta_data and see if it has a results field
    # if so, there's not work to do
    with open(meta_data_path, 'r') as f:
        meta_data = yaml.safe_load(f)
    # if 'results' in meta_data:
    #     return

    # otherwise get the results from the proccess logs
    # and write them to the meta-data
    results = start_end_stats(dirname)
    meta_data['results'] = results
    with open(meta_data_path, 'w') as f:
        yaml.safe_dump(meta_data, f)

def process_meta_data(dirname):
    '''Do some post-processing on the meta_data
    getting it ready for reporting.
    '''



    dirname = pathlib.Path(dirname)
    meta_data_path = dirname / 'meta-data.yaml'
    with open(meta_data_path, 'r') as f:
        meta_data = yaml.safe_load(f)

    # the number of files should be in the topdir name
    # it's not guaranteed, really, the files dir should get
    # its own meta_data file when it gets created

    # TODD check for a meta-data.yaml file in dirname

    files_dir_pos = meta_data['argv'].index('--files-dir') + 1
    files_dir = pathlib.Path(meta_data['argv'][files_dir_pos]).name
    files_per_process = int(files_dir.split('_')[-1])
    meta_data['files-per-process'] = files_per_process

    total_files = int(meta_data['num-procs']) * files_per_process
    meta_data['total-files'] = total_files
    meta_data['num-dirs'] = meta_data['num-procs']

    with open(meta_data_path, 'w') as f:
        yaml.safe_dump(meta_data, f)



def summarize_meta_data(dirname, header=False, separator=','):
    '''summarize the important parts of the meta_data.
    and return them as a line in a table.

    nodes, proceses, files per process, total files,
    files-per-sec average time, min time, max time, std dev,
    '''
    fields = [
        'num_nodes',
        'num_processes',
        'files_per_process',
        'total_files',
        'min',
        'max',
        'average',
        'median',
        'stddev',
    ]

    # TODO copy meta-data.yaml in case I mess it up



    # return fields as comma separated
    if header:
        return separator.join(fields)

    update_meta_data_results(dirname)
    process_meta_data(dirname)


    dirname = pathlib.Path(dirname)
    meta_data_path = dirname / 'meta-data.yaml'
    with open(meta_data_path, 'r') as f:
        meta_data = yaml.safe_load(f)

    results = meta_data['results']
    total_files = meta_data['total-files']

    data = [
        meta_data['num-nodes'],
        meta_data['num-procs'],
        meta_data['files-per-process'],
        total_files,
        total_files * results['min-inv-time'],
        total_files * results['max-inv-time'],
        total_files * results['average-inv-time'],
        total_files * results['median-inv-time'],
        total_files * results['stdev-inv-time'],
    ]

    return separator.join([str(d) for d in data])

def summarize_all(dirs, fileout):
    '''for a list of path do all the summaries
    print the summary lines to fileout.
    '''

    summary = []
    summary.append(summarize_meta_data(None, header=True))

    for d in dirs:
        try:
            print(d.name)
            summary.append(summarize_meta_data(d))
        except:
            print('fuck')
            continue

    print(summary)
    with open(fileout, 'w') as f:
        f.write('\n'.join(summary))



def summarize_stuff_now():
    '''cause you gotta get some results out'''
    d = pathlib.Path('/g/g0/defazio1/non-jira-projects/migration/data').glob("*")
    #print(list(d))
    d = [x for x in d if (x.name >= '2021-08-26_151411.616957' and x.name <= '2021-08-26_163113.065141/')]
    #for x in d:
    #    print(x.name)
    fileout = '/g/g0/defazio1/non-jira-projects/migration/data/summary-now'
    summarize_all(d, fileout)
