# force
Used to test out brute force hash

- bad
- dead
- b0000
- decaf
- deadbee

# Windows
I don't think this works on windows, something to do with the multithreading. Works on *nix / OSX

# How to use
From inside the Git Repo, run `python3 force.py`.

 - The script does not validate you provided a good hex value.
 - The script may get stuck forever trying to find you a match.
 - Short matches are almost instant (1 to 3 characters), 7 may or may not succeed at all due to the current search system.

In my first version of the script I would append an increasing integer to the commit message until the hash came out correct. But... then it was obvious something weird was going on.

The current version makes your commit look like it hasn't been touched at all; that it was pure coincidence that you ended up with this hash. It does this by adjusting the commit timestamp by +/- 500 seconds. This works well for shorter hash matches, but sometimes doesn't succeed for longer ones and just hangs (where as the incremental int approach always worked eventually).

