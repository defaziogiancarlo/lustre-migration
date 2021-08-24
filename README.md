## Data migration stuff

A useful idea may be to abstract doing stuff for srun.
The template seems to be something like:

Figure out what command needs to be run by `srun` and put it in a
file.
Figure out what srun command need to be run, and run it, and it will
use the command file you just mentioned.
Before running anything, collect all the metadata for the run and record
it in some east to read form.
Timestamp things.
Do basic setup, like creating all the directories that won't be created by
individual srun proccesses.
Then have all the srun processes put their results, and output in general,
into files.
Be able to quickly read and consolidate results, from the run meta data,
and the individual process results.

Maybe be able to reproduce a run, just from the given metadata file.
This might be difficult in practice, as the initial conditions probably
varies a lot depending on the experiment you are doing.
