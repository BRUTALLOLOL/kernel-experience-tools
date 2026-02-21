/**
 * core.cpp
 * Unified C++ core for kernel-experience-tools
 * 
 * Design principles:
 * 1. Heavy lifting in C++, Python for orchestration
 * 2. Batch evaluation to minimize Python call overhead
 * 3. Cache-friendly memory access patterns
 * 4. Automatic vectorization where possible
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
#include <pybind11/stl.h>
#include <vector>
#include <complex>
#include <algorithm>
#include <string>
#include <stdexcept>
#include <cstdint>

namespace py = pybind11;

// ============================================================================
// BATCH KERNEL EVALUATION - MINIMIZES PYTHON CALL OVERHEAD
// ============================================================================

/**
 * Evaluate kernel on a batch of time differences in one Python call.
 * Instead of calling Python for each (i,j) separately, we prepare an array
 * of tau values and get back an array of K(tau) values.
 * 
 * This reduces Python call overhead from O(n²) to O(n).
 */
py::array_t<double> evaluate_kernel_batch(
    py::function kernel_func,
    py::array_t<double> tau_array
) {
    auto tau = tau_array.unchecked<1>();
    int64_t n = tau.shape(0);
    
    // Single Python call for the entire batch
    py::array_t<double> result_array = kernel_func(tau_array);
    
    // Ensure result is the right shape and type
    if (result_array.size() != n) {
        throw std::runtime_error(
            "Kernel function must return array of same size as input"
        );
    }
    
    return result_array;
}

// ============================================================================
// OPTIMIZED VOLTERRA SOLVER WITH BATCH EVALUATION
// ============================================================================

/**
 * Solve Volterra equation using C++ with batch kernel evaluation.
 * 
 * Algorithm:
 * 1. Generate all unique tau = t[i] - t[j] values
 * 2. Evaluate kernel on all unique tau in ONE Python call
 * 3. Use precomputed K values for integration
 * 
 * This reduces Python calls from O(n²) to O(n) and enables vectorization.
 */
py::tuple solve_volterra_batch(
    py::function kernel_func,
    double t_max,
    int64_t n_points,
    double x0,
    const std::string& method = "trapezoidal"
) {
    // Create time grid
    std::vector<double> t(n_points);
    std::vector<double> x(n_points, 0.0);
    
    double dt = t_max / (n_points - 1);
    for (int64_t i = 0; i < n_points; ++i) {
        t[i] = i * dt;
    }
    
    x[0] = x0;
    
    // Generate all unique tau values needed
    // For Volterra equation, we need K(t[i] - t[j]) for all i >= j
    // These are just multiples of dt: 0, dt, 2*dt, ..., (n_points-1)*dt
    std::vector<double> unique_tau(n_points);
    for (int64_t k = 0; k < n_points; ++k) {
        unique_tau[k] = k * dt;
    }
    
    // Evaluate kernel on all unique tau in ONE Python call
    py::array_t<double> tau_array({n_points}, unique_tau.data());
    py::array_t<double> K_unique = evaluate_kernel_batch(kernel_func, tau_array);
    auto K_ptr = K_unique.unchecked<1>();
    
    // Pre-allocate K matrix in column-major order for better cache locality
    // We only need lower triangular, but storing full is simpler and still cache-friendly
    std::vector<double> K_matrix(n_points * n_points, 0.0);
    for (int64_t i = 0; i < n_points; ++i) {
        for (int64_t j = 0; j <= i; ++j) {
            // K(t[i] - t[j]) = K((i-j)*dt) = K_unique[i-j]
            K_matrix[i * n_points + j] = K_ptr[i - j];
        }
    }
    
    bool use_trapezoidal = (method == "trapezoidal");
    
    // Main integration loop - now working with precomputed K values
    for (int64_t i = 1; i < n_points; ++i) {
        double integral = 0.0;
        double* K_row = &K_matrix[i * n_points];
        
        if (use_trapezoidal) {
            // Trapezoidal rule - manually unrolled for better vectorization
            // First and last terms have weight 0.5, interior terms weight 1.0
            
            // First term (j=0)
            integral += 0.5 * dt * K_row[0] * x[0];
            
            // Interior terms
            #ifdef __GNUC__
            #pragma GCC ivdep  // Tell compiler it can vectorize
            #endif
            for (int64_t j = 1; j < i-1; ++j) {
                integral += dt * K_row[j] * x[j];
            }
            
            // Last term (j=i-1) - only if i>1
            if (i > 1) {
                integral += 0.5 * dt * K_row[i-1] * x[i-1];
            }
        } else {
            // Simple rectangular rule - can be fully vectorized
            #ifdef __GNUC__
            #pragma GCC ivdep
            #endif
            for (int64_t j = 0; j < i; ++j) {
                integral += dt * K_row[j] * x[j];
            }
        }
        
        x[i] = x0 - integral;
    }
    
    // Convert to Python objects
    return py::make_tuple(
        py::array_t<double>({n_points}, t.data()),
        py::array_t<double>({n_points}, x.data())
    );
}

// ============================================================================
// FAST N(T) COMPUTATION WITH VECTORIZED OPERATIONS
// ============================================================================

/**
 * Compute n(t) = log(x/x0) / log(lambda)
 * Vectorized implementation using explicit loops (compiler auto-vectorizes)
 */
py::object fast_n_vectorized(
    py::array_t<double> x_array,
    double x0,
    double lambda_param,
    bool return_complex
) {
    auto x = x_array.unchecked<1>();
    int64_t n = x.shape(0);
    
    double log_lambda = std::log(lambda_param);
    double inv_log_lambda = 1.0 / log_lambda;  // Multiply is faster than divide
    
if (return_complex) {
    std::vector<std::complex<double>> result(n);
    
    for (int64_t i = 0; i < n; ++i) {
        std::complex<double> z(x[i] / x0, 0.0);
        std::complex<double> log_z = std::log(z);
        result[i] = log_z * inv_log_lambda;
    }
    return py::cast(result);
}else {
        std::vector<double> result(n);
        const double min_ratio = 1e-12;
        
        #ifdef __GNUC__
        #pragma GCC ivdep
        #endif
        for (int64_t i = 0; i < n; ++i) {
            double ratio = x[i] / x0;
            if (ratio < min_ratio) ratio = min_ratio;
            result[i] = std::log(ratio) * inv_log_lambda;
        }
        return py::array_t<double>({n}, result.data());
    }
}

// ============================================================================
// FAST ENVELOPE WITH MOVING MAXIMUM (O(n) ALGORITHM)
// ============================================================================

py::array_t<double> fast_envelope_vectorized(
    py::array_t<double> x_array
) {
    auto x = x_array.unchecked<1>();
    int64_t n = x.shape(0);
    
    std::vector<double> result(n);
    double current_max = x[0];
    result[0] = current_max;
    
    for (int64_t i = 1; i < n; ++i) {
        if (x[i] > current_max) {
            current_max = x[i];
        }
        result[i] = current_max;
    }
    
    return py::array_t<double>({n}, result.data());
}

// ============================================================================
// FAST MONOTONIC MINIMUM (O(n) ALGORITHM)
// ============================================================================

py::array_t<double> monotonic_min_vectorized(
    py::array_t<double> n_array
) {
    auto n = n_array.unchecked<1>();
    int64_t len = n.shape(0);
    
    std::vector<double> result(len);
    double current_min = n[0];
    result[0] = current_min;
    
    for (int64_t i = 1; i < len; ++i) {
        if (n[i] < current_min) {
            current_min = n[i];
        }
        result[i] = current_min;
    }
    
    return py::array_t<double>({len}, result.data());
}

// ============================================================================
// HELPER: GENERATE TIME GRID (REUSABLE)
// ============================================================================

std::vector<double> generate_time_grid(double t_max, int64_t n_points) {
    std::vector<double> t(n_points);
    double dt = t_max / (n_points - 1);
    for (int64_t i = 0; i < n_points; ++i) {
        t[i] = i * dt;
    }
    return t;
}

// ============================================================================
// MODULE DEFINITIONS
// ============================================================================

#if defined(BUILD_SOLVERS_MODULE)

/**
 * Solvers module - optimized Volterra solvers
 */
PYBIND11_MODULE(_solvers_cpp, m) {
    m.doc() = "Optimized C++ solvers with batch kernel evaluation";
    
    m.def("solve_volterra", &solve_volterra_batch,
          "Fast Volterra solver with batch kernel evaluation (O(n) Python calls)",
          py::arg("kernel_func"),
          py::arg("t_max"),
          py::arg("n_points"),
          py::arg("x0") = 1.0,
          py::arg("method") = "trapezoidal");
    
    // Also expose the batch evaluator for advanced use
    m.def("evaluate_kernel_batch", &evaluate_kernel_batch,
          "Evaluate kernel on a batch of time differences in one Python call",
          py::arg("kernel_func"),
          py::arg("tau_array"));
}

#elif defined(BUILD_PROJECTION_MODULE)

/**
 * Projection module - vectorized projection algorithms
 */
PYBIND11_MODULE(_projection_cpp, m) {
    m.doc() = "Vectorized C++ projection algorithms";
    
    m.def("fast_n", &fast_n_vectorized,
          "Vectorized computation of n(t) = log(x/x0)/log(lambda)",
          py::arg("x"),
          py::arg("x0"),
          py::arg("lambda_param"),
          py::arg("return_complex") = false);
    
    m.def("fast_envelope", &fast_envelope_vectorized,
          "Fast O(n) envelope extraction (moving maximum)",
          py::arg("x"));
    
    m.def("monotonic_min", &monotonic_min_vectorized,
          "Fast O(n) monotonic minimum accumulation",
          py::arg("n"));
}

#else
#error "Must define either BUILD_SOLVERS_MODULE or BUILD_PROJECTION_MODULE"
#endif
