#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>

// Объявляем функцию из solvers.cpp (она уже включает реализацию)
py::tuple solve_volterra_cpp(
    py::function kernel_func,
    double t_max,
    int n_points,
    double x0,
    const std::string& method
);

// Модуль для pybind11
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
