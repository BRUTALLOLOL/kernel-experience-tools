/**
 * core.cpp
 * Unified C++ core for kernel-experience-tools
 * Contains both solvers and projection implementations
 */

// ABSOLUTELY FIRST - M_PI fix for Windows
#ifdef _WIN32
#define _USE_MATH_DEFINES
#endif
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <vector>
#include <complex>
#include <algorithm>
#include <string>

namespace py = pybind11;

// ============================================================================
// COMMON UTILITIES
// ============================================================================

// Any helper functions that might be used by both modules go here
// (none yet, but placeholder for future)

// ============================================================================
// SOLVERS IMPLEMENTATION
// ============================================================================

/**
 * Solve Volterra equation using C++ implementation
 * x(t) = x0 - ∫₀ᵗ K(t-τ) x(τ) dτ
 */
py::tuple solve_volterra_cpp(
    py::function kernel_func,
    double t_max,
    int n_points,
    double x0,
    const std::string& method
) {
    // Create time grid
    std::vector<double> t(n_points);
    std::vector<double> x(n_points);
    
    double dt = t_max / (n_points - 1);
    for (int i = 0; i < n_points; ++i) {
        t[i] = i * dt;
    }
    
    // Initial condition
    x[0] = x0;
    
    // Choose method
    bool use_trapezoidal = (method == "trapezoidal");
    
    // Main loop
    for (int i = 1; i < n_points; ++i) {
        double integral = 0.0;
        
        if (use_trapezoidal) {
            // Trapezoidal rule
            for (int j = 0; j < i; ++j) {
                double tj = t[j];
                double ti = t[i];
                
                // K(ti - tj)
                double K_val = kernel_func(ti - tj).cast<double>();
                
                if (j == 0) {
                    integral += 0.5 * dt * K_val * x[j];
                } else if (j == i-1) {
                    integral += 0.5 * dt * K_val * x[j];
                } else {
                    integral += dt * K_val * x[j];
                }
            }
        } else {
            // Rectangular rule (simpler but less accurate)
            for (int j = 0; j < i; ++j) {
                double tj = t[j];
                double ti = t[i];
                
                // K(ti - tj)
                double K_val = kernel_func(ti - tj).cast<double>();
                
                integral += dt * K_val * x[j];
            }
        }
        
        x[i] = x0 - integral;
    }
    
    // Convert to Python objects
    py::array_t<double> py_t = py::array_t<double>({n_points}, t.data());
    py::array_t<double> py_x = py::array_t<double>({n_points}, x.data());
    
    return py::make_tuple(py_t, py_x);
}

// ============================================================================
// PROJECTION IMPLEMENTATION
// ============================================================================

/**
 * Fast computation of n(t) = log(x/x0) / log(lambda)
 * with optional complex support
 */
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

/**
 * Fast envelope extraction via moving maximum
 * Simplified version - real implementation would use Hilbert transform
 */
py::array_t<double> fast_envelope(
    py::array_t<double> x_array
) {
    auto x = x_array.unchecked<1>();
    int n = x.shape(0);
    
    std::vector<double> result(n);
    
    double current_max = 0.0;
    for (int i = 0; i < n; ++i) {
        if (x[i] > current_max) {
            current_max = x[i];
        }
        result[i] = current_max;
    }
    
    return py::array_t<double>({n}, result.data());
}

/**
 * Fast monotonic minimum accumulation
 */
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

// ============================================================================
// MODULE DEFINITIONS
// ============================================================================

// For unified build approach, we use preprocessor directives
// to compile the same file into different modules

#if defined(BUILD_SOLVERS_MODULE)

/**
 * Solvers module - exports Volterra solver
 */
PYBIND11_MODULE(_solvers_cpp, m) {
    m.doc() = "C++ implementation of Volterra solvers for kernel-experience-tools";
    
    m.def("solve_volterra", &solve_volterra_cpp,
          "Solve Volterra equation x(t) = x0 - ∫₀ᵗ K(t-τ) x(τ) dτ",
          py::arg("kernel_func"),
          py::arg("t_max"),
          py::arg("n_points"),
          py::arg("x0") = 1.0,
          py::arg("method") = "trapezoidal");
}

#elif defined(BUILD_PROJECTION_MODULE)

/**
 * Projection module - exports fast projection algorithms
 */
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

#else
#error "Must define either BUILD_SOLVERS_MODULE or BUILD_PROJECTION_MODULE"
#endif
