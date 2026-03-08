
#pragma once
#include <string>
#include <vector>

struct GrepOptions {
    std::string              pattern;
    std::vector<std::string> files;
    bool   ignore_case    = false;
    bool   count_only     = false;
    bool   show_line_nums = true;
    bool   invert_match   = false;
    size_t chunk_size     = 64ULL * 1024 * 1024; // 64 MB
};

struct GrepResult {
    std::string filename;
    size_t      line_number;
    std::string line_content;
};

class CuGrep {
public:
    explicit CuGrep(const GrepOptions& opts);
    std::vector<GrepResult> run();
    bool had_error() const { return has_error_; }

private:
    GrepOptions opts_;
    bool        has_error_ = false; // Added error flag
    std::vector<GrepResult> search_file(const std::string& path);
};
