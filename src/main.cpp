
#include "cugrep.hpp"

#include <rmm/mr/device/pool_memory_resource.hpp>
#include <rmm/mr/device/cuda_memory_resource.hpp>
#include <rmm/mr/device/per_device_resource.hpp>

#include <iostream>
#include <map>
#include <cstring>

static void print_usage(const char* prog) {
    std::cerr
        << "Usage: " << prog << " [OPTIONS] PATTERN FILE...\n"
        << "  -i   Ignore case\n"
        << "  -c   Count matching lines only\n"
        << "  -v   Invert match (show non-matching lines)\n"
        << "  -n   Show line numbers (default: on)\n";
}

int main(int argc, char* argv[])
{
    if (argc < 3) { print_usage(argv[0]); return 1; }

    // \u2500\u2500 RMM memory pool (avoids repeated cudaMalloc overhead) \u2500\u2500
    rmm::mr::cuda_memory_resource                              cuda_mr;
    rmm::mr::pool_memory_resource<rmm::mr::cuda_memory_resource>
        pool_mr(&cuda_mr,
                32ULL * 1024 * 1024,    // initial pool: 32 MB
                512ULL * 1024 * 1024);  // max pool:    512 MB
    rmm::mr::set_current_device_resource(&pool_mr);

    // \u2500\u2500 Parse CLI \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    GrepOptions opts;
    int i = 1;
    while (i < argc && argv[i][0] == '-') {
        std::string flag = argv[i];
        if (flag == "-i") opts.ignore_case    = true;
        if (flag == "-c") opts.count_only     = true;
        if (flag == "-v") opts.invert_match   = true;
        if (flag == "-n") opts.show_line_nums = true;
        ++i;
    }

    if (i >= argc) { print_usage(argv[0]); return 1; }
    opts.pattern = argv[i++];
    while (i < argc) opts.files.push_back(argv[i++]);

    // \u2500\u2500 Run \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    CuGrep cugrep(opts);
    auto results = cugrep.run();

    // \u2500\u2500 Output \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    if (opts.count_only) {
        std::map<std::string, size_t> counts;
        for (auto& r : results) counts[r.filename]++;
        for (auto& [f, c] : counts)
            std::cout << f << ": " << c << "\n";
    } else {
        bool multi_file = opts.files.size() > 1;
        for (auto& r : results) {
            if (multi_file)          std::cout << r.filename << ":";
            if (opts.show_line_nums) std::cout << r.line_number << ":";
            std::cout << r.line_content << "\n";
        }
    }

    // Check for errors and return appropriate exit code
    if (cugrep.had_error()) {
        return 2; // Indicate an error occurred
    }

    return 0;
}
