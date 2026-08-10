# Git: copying a directory

Use these commands to copy a directory while preserving its contents.

## Copy a directory locally

```bash
git cp -r <source-directory> <destination-directory>
```

Example:

```bash
git cp -r docs/ old-docs/
```

## Copy a directory from one repository to another

If you want to copy a directory from another repository, first clone or fetch it, then copy the files from the desired path.

```bash
git clone <repository-url>
cp -r <repository>/path/to/dir ./path/to/target
```

## Notes

- `-r` is required for directories.
- If you are copying tracked files, make sure the destination path is correct before committing.
- For a Git-aware copy within the same repo, `git mv` is better for renaming or moving files.
