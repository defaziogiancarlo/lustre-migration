#!/bin/env python3

import os

# for x in os.environ:
#     if 'SLURM' in x:
#         print(f'{x}: {os.environ[x]}')
#print(os.environ['SLURM_PROCID'])
#print(os.environ['SLURM_NPROCS'])

print(f'procid:{os.environ["SLURM_PROCID"]} localid:{os.environ["SLURM_LOCALID"]} nodeid:{os.environ["SLURM_NODEID"]}')
