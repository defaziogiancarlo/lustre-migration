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


## More details after actually building the thing
The plan is that each subdirectory for each process not be striped, meaning
it's all on 1 MDT. Then for the migration, all the dirs are moved to another
MDT, so everything from MDT x to MDT y, with the same (x,y) for all proceses.

Also I need to increase the values `max_rpcs_in_flight` and  `max_mod_rpcs_in_flight`
on the clients, however for this to work I need to increase the value
`max_mod_rpcs_per_client` on the server, then reset all the connections.
Look these params up in the manual for how to set them.

## New idea: use dsync
Olaf made the point that lfs-migrate will preserve imporatant lustre metadata,
especially the fid, however, we don't care about presrving this metadata,
we just need some fid for each object. Because we're changing filesystems
and not just moving data around within a filesystem, the fids are all going to
change anyways. So why not try dsync? If copying files is just as fast,
copy with dsync instead of mmigrating with lfs-migrate? Also, dsync could
simplify the metadata/objects issue by doing both at the same time.

The question is, how fast is it? Realistically, it's probably the fastest thing
we've got that will put the files where they need to be for lustre
(zfs send/receive is very fast, but it won't give us the lustre setup we want
by itself).

So test how fast dsync can move files from a filesystem and back to itself via
pgarter on catalyst.
