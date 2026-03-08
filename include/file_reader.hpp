#pragma once
#include <string>
#include <vector>

class FileReader {
public:
    static std::vector<std::string>
        read_lines(const std::string& path);

    static std::vector<std::vector<std::string>>
        read_chunks(const std::string& path, size_t chunk_bytes);
};
