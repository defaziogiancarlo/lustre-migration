## lfs-migrate testing

Do some performance testing for lfs-migrate
The plan is to do some massive directories and see how long thigns take.

### Basic plan

The idea is to start with a directory that uses 2 MDTs and migrate it so that
it uses 4 MDTs.

The simple version would be a flat directory like `/p/lflood/defazio1/inode-migrate-test/`.
First, ensure that it is on 2 MDTs:
```bash
lfs migrate -m 0,2 /p/lflood/defazio1/inode-migrate-test/
```

Then, migrate the directory to all 4 MDTs:
```bash
lfs migrate -m 0,1,2,3 /p/lflood/defazio1/inode-migrate-test/
```

### Performance improvement?

One thing to check is whether or not lustre can be sped up by
having multiple migrates, for example,
if `/p/lflood/defazio1/inode-migrate-test/` has `n` subdirectories, could
I issue `n` lfs-migrate commands, one for each sub directory, and see a
performance improvement?

It's also possible to do individual files, so it might be worth it to
try to migrate only some fraction of the directory, because the rest of the
inodes are gonna end up on the current MDT, and don't need to be migrated.
My guess is that lfs-migrate is already smart enough to do this if you do:

```bash
lfs migrate -m 0 /p/lflood/defazio1/inode-migrate-test/
lfs migrate -m 0,1 /p/lflood/defazio1/inode-migrate-test/
```
Then for the second command, it just won't touch half the files.

## data to collect
The total number of files, the intitial striping and the final striping,
the number of processes used, the directory structure.

It may be useful to look at flat vs. deeply nested directories.

## create the initial data
use mdtest?
Create a directory with a ton of files, then migrate it to 2 MDTs
or set it up with `setstripe` to be on 2 MDTs

## from olaf
Yes.  It might be worthwhile to start with running mdtest to
create a directory tree, and then migrate those, just to validate your script.
And then you can do that with different directory sizes and see how directory
size affects migrate rate, if at all.
