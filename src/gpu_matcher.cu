#include "gpu_matcher.hpp"

#include <cudf/column/column.hpp>
#include <cudf/column/column_factories.hpp>
#include <cudf/strings/contains.hpp>
#include <cudf/strings/case.hpp>
#include <cudf/strings/strings_column_view.hpp>
#include <cudf/strings/regex/regex_program.hpp>

#include <rmm/cuda_stream_view.hpp>
#include <rmm/device_buffer.hpp>
#include <rmm/device_uvector.hpp>
#include <rmm/mr/device/per_device_resource.hpp>

#include <thrust/host_vector.h>
#include <thrust/device_ptr.h>
#include <thrust/copy.h>

#include <algorithm>
#include <cctype>
#include <vector>
#include <memory>

GpuMatcher::GpuMatcher(const std::string& pattern, bool ignore_case)
    : pattern_(pattern), ignore_case_(ignore_case) {}

static std::unique_ptr<cudf::strings::regex_program>
make_program(const std::string& pat)
{
    return cudf::strings::regex_program::create(
        pat,
        cudf::strings::regex_flags::DEFAULT,
        cudf::strings::capture_groups::NON_CAPTURE
    );
}

std::unique_ptr<cudf::column>
GpuMatcher::match_column(cudf::strings_column_view const& sv)
{
    if (ignore_case_) {
        auto lowered = cudf::strings::to_lower(sv);
        std::string lp = pattern_;
        std::transform(lp.begin(), lp.end(), lp.begin(),
                       [](unsigned char c){ return std::tolower(c); });
        auto prog = make_program(lp);
        return cudf::strings::contains_re(
            cudf::strings_column_view(lowered->view()), *prog);
    }
    auto prog = make_program(pattern_);
    return cudf::strings::contains_re(sv, *prog);
}

GpuMatcher::MatchResult
GpuMatcher::find_matches(const std::vector<std::string>& lines)
{
    if (lines.empty()) return {};

    auto  stream = rmm::cuda_stream_default;
    auto* mr     = rmm::mr::get_current_device_resource();

    // ── Build char buffer + offsets on host ───────────────────
    std::string          char_buf;
    std::vector<int32_t> offsets;
    offsets.reserve(lines.size() + 1);
    offsets.push_back(0);
    for (auto& s : lines) {
        char_buf += s;
        offsets.push_back(static_cast<int32_t>(char_buf.size()));
    }

    // ── Upload chars to device ────────────────────────────────
    rmm::device_buffer d_chars(
        char_buf.data(), char_buf.size(), stream, mr);

    // ── Upload offsets to device ──────────────────────────────
    rmm::device_uvector<int32_t> d_offsets(offsets.size(), stream, mr);
    cudaMemcpyAsync(
        d_offsets.data(), offsets.data(),
        offsets.size() * sizeof(int32_t),
        cudaMemcpyHostToDevice, stream.value());
    cudaStreamSynchronize(stream.value());

    // ── Build offsets column ──────────────────────────────────
    // Correct cudf::column constructor:
    // column(data_type, size_type, B1&& data,
    //        B2&& null_mask, size_type null_count,
    //        vector<unique_ptr<column>>&&)
    rmm::device_buffer offsets_data(
        d_offsets.data(),
        offsets.size() * sizeof(int32_t),
        stream, mr);

    auto offsets_col = std::make_unique<cudf::column>(
        cudf::data_type{cudf::type_id::INT32},
        static_cast<cudf::size_type>(offsets.size()),
        std::move(offsets_data),          // B1 data buffer
        rmm::device_buffer{},             // B2 null mask (empty = no nulls)
        0,                                // null count
        std::vector<std::unique_ptr<cudf::column>>{}  // children
    );

    // ── Build strings column ──────────────────────────────────
    auto col = cudf::make_strings_column(
        static_cast<cudf::size_type>(lines.size()),
        std::move(offsets_col),
        std::move(d_chars),
        0,    // null count
        {}    // null mask
    );

    // ── GPU regex match ───────────────────────────────────────
    cudf::strings_column_view sv_view(col->view());
    auto mask_col = match_column(sv_view);

    // ── Copy bool mask device → host ──────────────────────────
    size_t      n          = static_cast<size_t>(mask_col->size());
    const bool* d_bool_ptr = mask_col->view().data<bool>();

    thrust::host_vector<bool> h_mask(n);
    thrust::copy(
        thrust::device_pointer_cast(d_bool_ptr),
        thrust::device_pointer_cast(d_bool_ptr + n),
        h_mask.begin());

    // ── Collect results ───────────────────────────────────────
    MatchResult result;
    for (size_t i = 0; i < n; ++i) {
        if (h_mask[i]) {
            result.indices.push_back(i);
            result.lines.push_back(lines[i]);
        }
    }
    return result;
}
