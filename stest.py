#!/bin/env python3

import os

# for x in os.environ:
#     if 'SLURM' in x:
#         print(f'{x}: {os.environ[x]}')
print(os.environ['SLURM_PROCID'])
print(os.environ['SLURM_NPROCS'])
