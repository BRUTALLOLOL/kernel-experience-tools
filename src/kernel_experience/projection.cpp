/**
 * projection.cpp
 * Fast C++ implementations for heavy numerical parts of projection.py
 */

// ABSOLUTELY FIRST - before any includes
#ifdef _WIN32
#define _USE_MATH_DEFINES
#endif

#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include <complex>
#include <algorithm>

// Fallback if M_PI still not defined (shouldn't happen with _USE_MATH_DEFINES, but just in case)
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace py = pybind11;

// ----------------------------------------------------------------------------
// Fast computation of n(t) = log(x/x0) / log(lambda)
// with optional complex support
// ----------------------------------------------------------------------------
py::object fast_n_computation(
    py::array_t<double> x_array,
    double x0,
    double lambda_param,
    bool return_complex
) {
    auto x = x_array.unchecked<1>();
    int n = x.shape(0);
    
    double log_lambda = std::log(lambda_param);
    
    if (return_complex) {
        std::vector<std::complex<double>> result(n);
        for (int i = 0; i < n; ++i) {
            double ratio_real = x[i] / x0;
            double ratio_abs = std::abs(ratio_real);
            double ratio_angle = (ratio_real >= 0) ? 0.0 : M_PI;
            
            // Complex logarithm: ln(|r|) + i*arg(r)
            double real_part = std::log(ratio_abs) / log_lambda;
            double imag_part = ratio_angle / log_lambda;
            
            result[i] = std::complex<double>(real_part, imag_part);
        }
        return py::cast(result);
    } else {
        std::vector<double> result(n);
        for (int i = 0; i < n; ++i) {
            double ratio = std::max(x[i] / x0, 1e-12);
            result[i] = std::log(ratio) / log_lambda;
        }
        return py::array_t<double>({n}, result.data());
    }
}

// ----------------------------------------------------------------------------
// Fast envelope extraction via Hilbert transform
// Simplified version using FFT (real implementation would need FFTW)
// ----------------------------------------------------------------------------
py::array_t<double> fast_envelope(
    py::array_t<double> x_array
) {
    auto x = x_array.unchecked<1>();
    int n = x.shape(0);
    
    std::vector<double> result(n);
    
    // Simplified envelope: moving maximum (placeholder)
    // Real implementation would use FFT-based Hilbert transform
    double current_max = 0.0;
    for (int i = 0; i < n; ++i) {
        if (x[i] > current_max) {
            current_max = x[i];
        }
        result[i] = current_max;
    }
    
    return py::array_t<double>({n}, result.data());
}

// ----------------------------------------------------------------------------
// Fast monotonic minimum accumulation
// ----------------------------------------------------------------------------
py::array_t<double> fast_monotonic_min(
    py::array_t<double> n_array
) {
    auto n = n_array.unchecked<1>();
    int len = n.shape(0);
    
    std::vector<double> result(len);
    double current_min = n[0];
    
    for (int i = 0; i < len; ++i) {
        if (n[i] < current_min) {
            current_min = n[i];
        }
        result[i] = current_min;
    }
    
    return py::array_t<double>({len}, result.data());
}

// ----------------------------------------------------------------------------
// Module definition
// ----------------------------------------------------------------------------
PYBIND11_MODULE(_projection_cpp, m) {
    m.doc() = "C++ acceleration for projection algorithms";
    
    m.def("fast_n", &fast_n_computation,
          "Fast computation of n(t) = log(x/x0)/log(lambda)",
          py::arg("x"),
          py::arg("x0"),
          py::arg("lambda_param"),
          py::arg("return_complex") = false);
    
    m.def("fast_envelope", &fast_envelope,
          "Fast envelope extraction",
          py::arg("x"));
    
    m.def("fast_monotonic_min", &fast_monotonic_min,
          "Fast monotonic minimum accumulation",
          py::arg("n"));
}
