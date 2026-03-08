
# CuGrep - GPU Accelerated Grep Tool

CuGrep is a high-performance `grep` utility that leverages NVIDIA GPUs and the cuDF library from RAPIDS to accelerate pattern matching in large text datasets. It's designed for speed-critical applications where traditional CPU-based `grep` might be too slow.

## Features

- **GPU Accelerated**: Utilizes cuDF for high-performance string matching on NVIDIA GPUs.
- **Regex Support**: Supports standard regular expressions for flexible pattern matching.
- **Case Insensitive Search**: Option to perform case-insensitive searches.
- **Invert Match**: Find lines that *do not* match the pattern.
- **Line Numbers**: Display line numbers for matched (or non-matched) lines.
- **Count Only**: Only output the count of matching lines.

## Installation

### Prerequisites

- NVIDIA GPU with CUDA compatibility (Compute Capability 7.0+ recommended)
- CUDA Toolkit (version 11.5+ recommended)
- cuDF library from RAPIDS (see [RAPIDS installation guide](https://docs.rapids.ai/install) for details)
- CMake (version 3.23+)
- GCC (version 9+)

### Building from Source

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-repo/cugrep.git # Replace with actual repo URL
    cd cugrep
    ```

2.  **Create a build directory and configure CMake**:

    ```bash
    mkdir build
    cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_CUDA_ARCHITECTURES="75" \
             -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
             -DCMAKE_PREFIX_PATH="/path/to/cudf/cmake/config;/path/to/rmm/cmake/config"
    ```

    *   Adjust `CMAKE_CUDA_ARCHITECTURES` to your GPU's compute capability (e.g., `70`, `80`, `86`).
    *   Ensure `CMAKE_CUDA_COMPILER` points to your `nvcc` executable.
    *   `CMAKE_PREFIX_PATH` should include paths to your cuDF and RMM CMake configuration files.

3.  **Build the executable**:

    ```bash
    make -j$(nproc)
    ```

    The `cugrep` executable will be created in the `build/` directory.

## Usage

The `cugrep` executable can be run directly from the command line:

```bash
./build/cugrep [OPTIONS] PATTERN FILE...
```

**Example: Basic search**

```bash
./build/cugrep "error" /path/to/logfile.txt
```

For more details on available options, run `./build/cugrep --help`.

## Contributing

We welcome contributions to CuGrep! If you're interested in improving this project, please follow these guidelines:

1.  **Fork the repository** and clone your fork.
2.  **Create a new branch** for your feature or bug fix.
3.  **Make your changes**, adhering to the existing coding style.
4.  **Write unit tests** for new features or bug fixes.
5.  **Ensure all tests pass** locally.
6.  **Commit your changes** with clear and concise messages.
7.  **Push your branch** to your fork.
8.  **Open a Pull Request** to the `main` branch of the original repository, providing a detailed description of your changes.

## Benchmarking Guidelines

To ensure consistent and reproducible benchmarking results across different GPU architectures and environments, please follow these guidelines:

1.  **Specify Hardware**: Clearly state the GPU model(s), CPU, and memory configuration used for benchmarking.
2.  **Software Environment**: Detail the CUDA Toolkit version, cuDF version, compiler (GCC/Clang version), and operating system.
3.  **Dataset Characteristics**: Provide information about the dataset used, including its size, number of lines, average line length, and the nature of the patterns being searched (e.g., regex complexity, frequency of matches).
4.  **Configuration**: Document any specific `CuGrep` options (e.g., `--ignore-case`, `--chunk-size`) and RMM memory pool settings used.
5.  **Metrics**: Report relevant performance metrics such as execution time (wall-clock time), GPU utilization, and memory usage. Run benchmarks multiple times and report average/median values to account for variability.
6.  **Isolation**: Ensure benchmarks are run in an isolated environment to minimize interference from other processes.

By following these guidelines, we can better compare and understand the performance characteristics of CuGrep across various setups.

## License

CuGrep is licensed under the Apache 2.0 License. See the `LICENSE` file for more details.
