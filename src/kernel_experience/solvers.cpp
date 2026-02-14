/**
 * Numerical solvers for Volterra integral equations.
 * C++ implementation matching the Python version exactly.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <vector>
#include <string>
#include <stdexcept>

namespace py = pybind11;

/**
 * Solve x(t) = x0 - ∫₀ᵗ K(t-τ) x(τ) dτ.
 *
 * @param kernel_func Python callable for memory kernel K(t)
 * @param t_max Maximum time
 * @param n_points Number of time points
 * @param x0 Initial condition
 * @param method Integration method ('trapezoidal' or 'simpson')
 * @return Tuple of (time grid, solution x(t)) as numpy arrays
 */
py::tuple solve_volterra_cpp(
    py::function kernel_func,
    double t_max,
    int n_points,
    double x0,
    const std::string& method = "trapezoidal"
) {
    // Create time grid: t = linspace(0, t_max, n_points)
    std::vector<double> t(n_points);
    double dt = t_max / (n_points - 1);
    for (int i = 0; i < n_points; ++i) {
        t[i] = i * dt;
    }

    // Solution array: x = zeros(n_points); x[0] = x0
    std::vector<double> x(n_points, 0.0);
    x[0] = x0;

    // Precompute kernel values for efficiency: K_vals[i, j] = kernel(t[i] - t[j])
    // Using vector of vectors to store lower triangular part
    std::vector<std::vector<double>> K_vals(n_points);
    for (int i = 0; i < n_points; ++i) {
        K_vals[i].resize(i + 1);
        for (int j = 0; j <= i; ++j) {
            double tau = t[i] - t[j];
            py::object result = kernel_func(tau);
            K_vals[i][j] = result.cast<double>();
        }
    }

    // Solve using specified method
    if (method == "trapezoidal") {
        // Trapezoidal rule implementation
        for (int i = 1; i < n_points; ++i) {
            double integral = 0.0;
            for (int j = 0; j < i; ++j) {
                // Weight: 0.5 for endpoints, 1.0 for interior points
                double weight = (j == 0 || j == i - 1) ? 0.5 : 1.0;
                integral += weight * K_vals[i][j] * x[j] * dt;
            }
            x[i] = x0 - integral;
        }
    }
    else if (method == "simpson") {
        // Simpson's rule implementation
        for (int i = 1; i < n_points; ++i) {
            if (i % 2 == 0) {
                // Simpson's rule applies for even number of intervals
                double integral = K_vals[i][0] * x[0] + K_vals[i][i] * x[i-1];
                for (int j = 1; j < i; ++j) {
                    // Weight: 4 for odd indices, 2 for even indices (excluding endpoints)
                    double weight = (j % 2 == 1) ? 4.0 : 2.0;
                    integral += weight * K_vals[i][j] * x[j];
                }
                integral *= dt / 3.0;
                x[i] = x0 - integral;
            } else {
                // Fall back to trapezoidal for odd number of intervals
                double integral = 0.0;
                for (int j = 0; j < i; ++j) {
                    double weight = (j == 0 || j == i - 1) ? 0.5 : 1.0;
                    integral += weight * K_vals[i][j] * x[j] * dt;
                }
                x[i] = x0 - integral;
            }
        }
    }
    else {
        throw std::invalid_argument("Method must be 'trapezoidal' or 'simpson'");
    }

    // Return as numpy arrays
    return py::make_tuple(
        py::array_t<double>({n_points}, t.data()),
        py::array_t<double>({n_points}, x.data())
    );
}

// Module definition for pybind11
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
