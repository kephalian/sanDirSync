
#  Santhosh Directory Synchronizer

A Python script for synchronizing directories with options for verbose logging, purging, forced copying, and two-way synchronization. Additionally, it can verify file integrity using MD5 hashes. This is an modified version of Dirsync module available in Python pypi based on Robocopy.

[https://pypi.org/project/dirsync/](https://pypi.org/project/dirsync/)
## Features

- **One-way Synchronization**: Synchronize files from source to destination.
- **Two-way Synchronization**: Ensure both source and destination directories are in sync.
- **MD5 Verification**: Compute and compare MD5 hashes for all files in source and destination to verify integrity.
- **Verbose Mode**: Output detailed log messages during the synchronization process.
- **Purge Mode**: Delete files in the destination that are not present in the source.
- **Force Copy Mode**: Always copy files even if they appear unchanged.
- **Use Content Mode**: Compare file contents instead of metadata.

## Usage

```bash
python sync.py <source_directory> <destination_directory> [options]
```

### Options

- `--verbose`: Enable verbose logging.
- `--purge`: Delete files in the destination that are not present in the source.
- `--forcecopy`: Always copy files even if they appear unchanged.
- `--use-ctime`: Use creation time for comparison (default is modification time).
- `--use-content`: Compare file contents instead of metadata.
- `--2sync`: Enable two-way synchronization.
- `--hverify`: Compute and compare MD5 hashes for all files to verify integrity.

### Example

```bash
python sync.py /path/to/source /path/to/destination --verbose --purge --2sync --hverify
```

This command will:
- Synchronize files between `/path/to/source` and `/path/to/destination`.
- Delete files in the destination that are not present in the source.
- Perform two-way synchronization.
- Compute and compare MD5 hashes for all files to ensure integrity.
- Output detailed log messages during the synchronization process.

## Requirements

- Python 3.x

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/directory-synchronizer.git
cd directory-synchronizer
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are always welcome!!
