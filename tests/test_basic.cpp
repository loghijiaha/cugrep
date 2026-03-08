#include "file_reader.hpp"
#include <cassert>
#include <fstream>
#include <iostream>

int main() {
    // Write a small temp file
    const std::string path = "/tmp/cugrep_test.txt";
    {
        std::ofstream f(path);
        f << "hello world\n";
        f << "error found\n";
        f << "all good\n";
        f << "another error here\n";
    }

    auto lines = FileReader::read_lines(path);
    assert(lines.size() == 4);
    assert(lines[0] == "hello world");
    assert(lines[1] == "error found");

    std::cout << "test_basic PASSED\n";
    return 0;
}
