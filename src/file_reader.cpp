#include "file_reader.hpp"
#include <fstream>
#include <stdexcept>

std::vector<std::string>
FileReader::read_lines(const std::string& path)
{
    std::ifstream f(path);
    if (!f.is_open())
        throw std::runtime_error("Cannot open file: " + path);

    std::vector<std::string> lines;
    std::string line;
    while (std::getline(f, line))
        lines.push_back(std::move(line));
    return lines;
}

std::vector<std::vector<std::string>>
FileReader::read_chunks(const std::string& path, size_t chunk_bytes)
{
    auto all = read_lines(path);
    std::vector<std::vector<std::string>> chunks;

    size_t start = 0;
    while (start < all.size()) {
        size_t bytes = 0, end = start;
        while (end < all.size() && bytes < chunk_bytes)
            bytes += all[end++].size() + 1;

        chunks.emplace_back(all.begin() + start, all.begin() + end);
        start = end;
    }
    return chunks;
}
