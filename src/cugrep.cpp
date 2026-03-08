
#include "cugrep.hpp"
#include "gpu_matcher.hpp"
#include "file_reader.hpp"

#include <set>
#include <stdexcept>
#include <iostream>

CuGrep::CuGrep(const GrepOptions& opts) : opts_(opts) {}

std::vector<GrepResult> CuGrep::run()
{
    std::vector<GrepResult> all;
    for (const auto& f : opts_.files) {
        try {
            auto r = search_file(f);
            all.insert(all.end(), r.begin(), r.end());
        } catch (const std::exception& e) {
            std::cerr << "Error reading " << f << ": " << e.what() << "\n";
            has_error_ = true; // Set error flag
        }
    }
    return all;
}

std::vector<GrepResult>
CuGrep::search_file(const std::string& filepath)
{
    GpuMatcher matcher(opts_.pattern, opts_.ignore_case);
    auto chunks = FileReader::read_chunks(filepath, opts_.chunk_size);

    std::vector<GrepResult> results;
    size_t line_offset = 0;

    for (auto& chunk : chunks) {
        auto mr = matcher.find_matches(chunk);

        if (!opts_.invert_match) {
            for (size_t k = 0; k < mr.indices.size(); ++k)
                results.push_back({
                    filepath,
                    line_offset + mr.indices[k] + 1,
                    mr.lines[k]
                });
        } else {
            std::set<size_t> matched(mr.indices.begin(), mr.indices.end());
            for (size_t i = 0; i < chunk.size(); ++i)
                if (!matched.count(i))
                    results.push_back({
                        filepath,
                        line_offset + i + 1,
                        chunk[i]
                    });
        }
        line_offset += chunk.size();
    }
    return results;
}
