#pragma once
#include <string>
#include <vector>
#include <memory>
#include <cudf/column/column.hpp>
#include <cudf/strings/strings_column_view.hpp>

class GpuMatcher {
public:
    explicit GpuMatcher(const std::string& pattern,
                        bool ignore_case = false);

    struct MatchResult {
        std::vector<size_t>      indices;
        std::vector<std::string> lines;
    };

    MatchResult find_matches(const std::vector<std::string>& lines);

private:
    std::string pattern_;
    bool        ignore_case_;

    std::unique_ptr<cudf::column>
        match_column(cudf::strings_column_view const& sv);
};
