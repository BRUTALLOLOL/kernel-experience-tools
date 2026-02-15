/**
 * core.cpp
 * Unified C++ core - does heavy lifting, Python does the thinking
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <vector>
#include <complex>
#include <cmath>

namespace py = pybind11;

// ============================================================================
// 1. C++ SOLVER - HEAVY LIFTING
// ============================================================================

py::tuple solve_volterra_cpp(
    py::function kernel_func,  // Python calls this with C++ speed
    double t_max,
    int n_points,
    double x0,
    const std::string& method
) {
    std::vector<double> t(n_points);
    std::vector<double> x(n_points);
    
    double dt = t_max / (n_points - 1);
    for (int i = 0; i < n_points; ++i) t[i] = i * dt;
    x[0] = x0;
    
    bool use_trapezoidal = (method == "trapezoidal");
    
    // MAIN LOOP - C++ calls Python function, but that's OK
    // because Python function is fast (it's just math)
    for (int i = 1; i < n_points; ++i) {
        double integral = 0.0;
        
        for (int j = 0; j < i; ++j) {
            double tau = t[i] - t[j];
            double K_val = kernel_func(tau).cast<double>();  // ← Python call
            
            if (use_trapezoidal) {
                double w = (j == 0 || j == i-1) ? 0.5 : 1.0;
                integral += w * dt * K_val * x[j];
            } else {
                integral += dt * K_val * x[j];
            }
        }
        x[i] = x0 - integral;
    }
    
    return py::make_tuple(
        py::array_t<double>({n_points}, t.data()),
        py::array_t<double>({n_points}, x.data())
    );
}

// ============================================================================
// 2. FAST N(T) COMPUTATION - PURE C++
// ============================================================================

py::object fast_n_cpp(
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
            double r = x[i] / x0;
            result[i] = std::complex<double>(
                std::log(std::abs(r)) / log_lambda,
                std::arg(r) / log_lambda
            );
        }
        return py::cast(result);
    } else {
        std::vector<double> result(n);
        for (int i = 0; i < n; ++i) {
            double r = std::max(x[i] / x0, 1e-12);
            result[i] = std::log(r) / log_lambda;
        }
        return py::array_t<double>({n}, result.data());
    }
}

// ============================================================================
// 3. ENVELOPE - PURE C++
// ============================================================================

py::array_t<double> fast_envelope_cpp(py::array_t<double> x_array) {
    auto x = x_array.unchecked<1>();
    int n = x.shape(0);
    std::vector<double> result(n);
    double current_max = 0.0;
    for (int i = 0; i < n; ++i) {
        if (x[i] > current_max) current_max = x[i];
        result[i] = current_max;
    }
    return py::array_t<double>({n}, result.data());
}

// ============================================================================
// 4. MONOTONIC MIN - PURE C++
// ============================================================================

py::array_t<double> monotonic_min_cpp(py::array_t<double> n_array) {
    auto n = n_array.unchecked<1>();
    int len = n.shape(0);
    std::vector<double> result(len);
    double current_min = n[0];
    for (int i = 0; i < len; ++i) {
        if (n[i] < current_min) current_min = n[i];
        result[i] = current_min;
    }
    return py::array_t<double>({len}, result.data());
}

// ============================================================================
// MODULE DEFINITIONS
// ============================================================================

#if defined(BUILD_SOLVERS_MODULE)
PYBIND11_MODULE(_solvers_cpp, m) {
    m.doc() = "C++ heavy lifting for Volterra solvers";
    m.def("solve_volterra", &solve_volterra_cpp,
          "Fast Volterra solver - calls Python kernel function",
          py::arg("kernel_func"),
          py::arg("t_max"),
          py::arg("n_points"),
          py::arg("x0") = 1.0,
          py::arg("method") = "trapezoidal");
}

#elif defined(BUILD_PROJECTION_MODULE)
PYBIND11_MODULE(_projection_cpp, m) {
    m.doc() = "C++ heavy lifting for projections";
    m.def("fast_n", &fast_n_cpp,
          py::arg("x"), py::arg("x0"), py::arg("lambda_param"), 
          py::arg("return_complex") = false);
    m.def("fast_envelope", &fast_envelope_cpp, py::arg("x"));
    m.def("monotonic_min", &monotonic_min_cpp, py::arg("n"));
}

#else
#error "Must define BUILD_SOLVERS_MODULE or BUILD_PROJECTION_MODULE"
#endif
