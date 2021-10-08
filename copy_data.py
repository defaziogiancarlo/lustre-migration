'''This should be the one big file that has all the stuff.
Can do a whole set of dsync runs,
then analyze them,
then graph them.











Command template:
the commands that you will be modifying using some function
mdtest

Srun template:
srun -N {num_nodes} -n {num_procs}



important yaml data:

striping data from source and destination

srun command
dsync command

results location

meta-data about structure of tree



'''

# configurables:
# where to make the trees
# where to store the results

# make tree


srun_template = 'srun -p {parition} -N {num_nodes} -n {num_procs} -l {command}'

def srun_generator(template, num_nodes=1, num_procs=1):
    '''generate a sequence of srun commands'''
    # if only an int given, change it into a sequence of length 1
    if isinstance(num_nodes, int):
        num_nodes = tuple(num_nodes)
    if isinstance(num_procs, int):
        num_procs = tuple(num_procs)

    for node_value in num_nodes:
        for proc_value in num_procs:
            if node_value <= proc_value:
                yield template.format(
                    num_nodes=node_value,
                    num_procs=proc_value
                )

class DsyncSrunner:

    def __init__(
            self,
            srun_template=None,
            command_template=None,

    ):
