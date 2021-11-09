#!/usr/bin/bash

# create files
MDTEST=/g/g0/defazio1/repos/ior/src/mdtest
srun --nodes 2 --ntasks 4 --partition pgarter $MDTEST -C -n 10 -w 8192 -d "/p/lustre1/defazio1/"


# run the migrate

# process the results
