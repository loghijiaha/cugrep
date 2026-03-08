
# PyCuGrep

PyCuGrep is a Python package that provides a GPU-accelerated `grep` utility, leveraging the power of NVIDIA GPUs and the cuDF library from RAPIDS. It's designed for rapidly searching large text files or datasets by offloading the pattern matching to the GPU, significantly speeding up operations compared to traditional CPU-based `grep` for suitable workloads.

## Features

- **GPU Accelerated**: Utilizes cuDF for high-performance string matching on NVIDIA GPUs.
- **Regex Support**: Supports standard regular expressions for flexible pattern matching.
- **Case Insensitive Search**: Option to perform case-insensitive searches.
- **Invert Match**: Find lines that *do not* match the pattern.
- **Line Numbers**: Display line numbers for matched (or non-matched) lines.
- **Count Only**: Only output the count of matching lines.

## Installation

To install `pycugrep`, you'll need a system with an NVIDIA GPU and CUDA installed. It's recommended to install via pip:

```bash
pip install pycugrep
```

## Usage

PyCuGrep can be used directly from the command line after installation:

```bash
cugrep [OPTIONS] PATTERN FILE...
```

**Example: Basic search**

```bash
cugrep "error" /path/to/logfile.txt
```

**Example: Case-insensitive search across multiple files**

```bash
cugrep -i "warning" file1.txt file2.txt
```

**Example: Count only, inverted match**

```bash
cugrep -c -v "success" all_logs.txt
```

For more details on available options, run `cugrep --help`.

## Development

For local development, after cloning the repository, navigate to the `python/` directory and install in editable mode:

```bash
cd cugrep/python
pip install -e .
```

## License

PyCuGrep is licensed under the Apache 2.0 License. See the `LICENSE` file for more details.
