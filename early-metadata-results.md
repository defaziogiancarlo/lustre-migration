## Early results for metadata testing
These results were done using catalyst and garter (lflood)

The basic task is to create a bunch of files in a bunch of
directories, distribute them across 2 MDTs using lfs-migrate,
then spread them onto all 4 MDTs.

That last step is 2 to 4 MDTs, is the most important, because it's what
we expect to have to do for the actual migration.

The test environment is a directory with
256 subdirectories
each of which contains 512 empty files.
So there are 256 * 512 = 131072 files,
and I believe that the directories are moved too, so 256 directories.

The test is to see if the filesystem scales with processes.
That is, does having a bunch of processes. potentially on a bunch of nodes,
speed things up, or will I reach some limit, or at least diminishing returns,
as I up the number of simultaneous lfs-migrates in progress.

Fore the data, each process does one directory, so fewer processes will do
files, but the number of total files is always (num_proceses * 512)

data:
nodes        processes        rate (files/sec)
16            256                537
8             128                458
4             64                 ? error
1               1                49
1               1                48 (4 directories consecutively)
