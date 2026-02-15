/**
 * projections.cpp
 * C++ implementations of heavy kernel projections.
 * Used as a performance drop-in replacement for Python versions.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <vector>
#include <cmath>
#include <stdexcept>
#include <string>

namespace py = pybind11;

// ----------------------------------------------------------------------------
// Cross-platform gamma function
// ----------------------------------------------------------------------------
double tgamma_safe(double x) {
    #ifdef _WIN32
        // Simple Lanczos approximation for Windows
        static const double coeff[] = {
            1.000000000190015, 76.18009172947146, -86.50532032941677,
            24.01409824083091, -1.231739572450155, 0.1208650973866179e-2,
            -0.5395239384953e-5
        };
        double y = x;
        double tmp = x + 5.5;
        tmp -= (x + 0.5) * std::log(tmp);
        double ser = 1.000000000190015;
        for (int i = 1; i <= 6; ++i) {
            y += 1.0;
            ser += coeff[i] / y;
        }
        return std::exp(-tmp + std::log(2.5066282746310005 * ser / x));
    #else
        return std::tgamma(x);
    #endif
}

// ----------------------------------------------------------------------------
// 1. DISTRIBUTED ORDER KERNEL
// K(t) = ∫ w(α) * t^(-α) / Γ(1-α) * exp(-βt) dα
// ----------------------------------------------------------------------------
py::array_t<double> distributed_order_cpp(
    py::array_t<double> t_array,
    py::array_t<double> alphas_array,
    py::array_t<double> weights_array,
    double beta = 0.3,
    bool temper = true,
    bool oscillate = false
) {
    auto t = t_array.unchecked<1>();
    auto alphas = alphas_array.unchecked<1>();
    auto weights = weights_array.unchecked<1>();
    
    int n_t = t.shape(0);
    int n_alpha = alphas.shape(0);
    
    if (n_alpha != weights.shape(0)) {
        throw std::invalid_argument("alphas and weights must have same length");
    }
    
    std::vector<double> result(n_t, 0.0);
    
    for (int i = 0; i < n_t; ++i) {
        double ti = t[i];
        if (ti < 1e-15) ti = 1e-15;
        
        double sum = 0.0;
        for (int j = 0; j < n_alpha; ++j) {
            double a = alphas[j];
            double w = weights[j];
            
            // Base term: t^(-a) / Γ(1-a)
            double term = w * std::pow(ti, -a) / tgamma_safe(1.0 - a);
            
            // Optional tempering
            if (temper) {
                term *= std::exp(-beta * ti);
            }
            
            // Optional deterministic oscillations (for testing)
            if (oscillate) {
                term *= (1.0 + 0.2 * std::sin(13.0 * ti) + 
                               0.2 * std::sin(47.0 * ti) + 
                               0.2 * std::sin(127.0 * ti));
            }
            
            sum += term;
        }
        
        // Normalize by dα (assumes uniform spacing)
        double dα = (alphas[n_alpha-1] - alphas[0]) / (n_alpha - 1);
        result[i] = sum * dα;
    }
    
    return py::array_t<double>({n_t}, result.data());
}

// ----------------------------------------------------------------------------
// 2. TEMPERED POWER-LAW KERNEL (special case)
// K(t) = γ * t^(α-1) * e^(-βt) / Γ(α)
// ----------------------------------------------------------------------------
py::array_t<double> tempered_power_law_cpp(
    py::array_t<double> t_array,
    double alpha,
    double beta,
    double gamma = 1.0
) {
    auto t = t_array.unchecked<1>();
    int n_t = t.shape(0);
    
    std::vector<double> result(n_t, 0.0);
    double norm = gamma / tgamma_safe(alpha);
    
    for (int i = 0; i < n_t; ++i) {
        double ti = t[i];
        if (ti < 1e-15) ti = 1e-15;
        result[i] = norm * std::pow(ti, alpha - 1.0) * std::exp(-beta * ti);
    }
    
    return py::array_t<double>({n_t}, result.data());
}

// ----------------------------------------------------------------------------
// 3. PRABHAKAR KERNEL (simplified core)
// K(t) = t^(β-1) * E_{α,β}^δ(-t^α)
// C++ implementation of the core part (without full Mittag-Leffler)
// ----------------------------------------------------------------------------
py::array_t<double> prabhakar_core_cpp(
    py::array_t<double> t_array,
    double alpha,
    double beta,
    double delta
) {
    auto t = t_array.unchecked<1>();
    int n_t = t.shape(0);
    
    std::vector<double> result(n_t, 0.0);
    
    for (int i = 0; i < n_t; ++i) {
        double ti = t[i];
        if (ti < 1e-15) ti = 1e-15;
        
        // Simplified Prabhakar core (full implementation would need ML function)
        // For now, returns just the power-law part
        result[i] = std::pow(ti, beta - 1.0);
    }
    
    return py::array_t<double>({n_t}, result.data());
}

// ----------------------------------------------------------------------------
// Python module definition
// ----------------------------------------------------------------------------
PYBIND11_MODULE(_projections_cpp, m) {
    m.doc() = "C++ implementations of heavy kernel projections with Python fallback";
    
    m.def("distributed_order", &distributed_order_cpp,
          "Fast distributed order kernel computation",
          py::arg("t"),
          py::arg("alphas"),
          py::arg("weights"),
          py::arg("beta") = 0.3,
          py::arg("temper") = true,
          py::arg("oscillate") = false);
    
    m.def("tempered_power_law", &tempered_power_law_cpp,
          "Fast tempered power-law kernel",
          py::arg("t"),
          py::arg("alpha"),
          py::arg("beta"),
          py::arg("gamma") = 1.0);
    
    m.def("prabhakar_core", &prabhakar_core_cpp,
          "Core part of Prabhakar kernel (simplified)",
          py::arg("t"),
          py::arg("alpha"),
          py::arg("beta"),
          py::arg("delta"));
}
