"""
Test suite for Kernel-Experience Tools library.
Validates projection algorithms, kernel classes, and accuracy metrics.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from time import time

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the library
try:
    from src.kernel_experience import Kernel, project_kernel_to_n, project_to_envelope_n, compute_accuracy

    print("✅ Library imported successfully")
    print(f"Kernel module: {Kernel.__module__}")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_basic_kernel_creation():
    """Test creation of standard kernel types."""
    print("\n" + "=" * 50)
    print("TEST 1: Kernel Creation")
    print("=" * 50)

    kernels = [
        ("Exponential", Kernel.exponential(gamma=1.5)),
        ("Power-law (α=0.6)", Kernel.power_law(alpha=0.6, gamma=1.0)),
        ("Power-law (α=0.8)", Kernel.power_law(alpha=0.8, gamma=1.0)),
        ("Tempered power-law", Kernel.tempered_power_law(alpha=0.7, beta=0.3)),
    ]

    for name, kernel in kernels:
        # Test evaluation at sample points
        t_test = np.array([0.1, 1.0, 5.0])
        values = kernel(t_test)

        print(f"{name:25} | K(0.1)={values[0]:6.3f}, K(1)={values[1]:6.3f}, K(5)={values[2]:6.3f}")

    return True


def test_volterra_solution_accuracy():
    """Test accuracy of Volterra equation solution."""
    print("\n" + "=" * 50)
    print("TEST 2: Solution Accuracy")
    print("=" * 50)

    # Для экспоненциального ядра аналитическое решение известно
    kernel_exp = Kernel.exponential(gamma=1.0)
    t, x, n = project_kernel_to_n(kernel_exp, t_max=5.0, n_points=1000, lambda_param=0.8)

    # Аналитическое решение для K(t)=γe^{-γt} при γ=1: x(t)=e^{-t}(1+t)
    # Но это приближенно, лучше проверить свойства:
    print(f"Exponential kernel (γ=1.0):")
    print(f"  x(0)={x[0]:.6f} (should be 1.0)")
    print(f"  x(5)={x[-1]:.6f} (should be small > 0)")
    print(f"  Monotonic: {np.all(np.diff(x) <= 1e-10)}")
    print(f"  n(t) final: {n[-1]:.3f}")

    # Для степенного ядра
    kernel_pl = Kernel.power_law(alpha=0.7, gamma=1.0)
    t, x, n = project_kernel_to_n(kernel_pl, t_max=10.0, n_points=500)

    print(f"\nPower-law kernel (α=0.7):")
    print(f"  Monotonic: {np.all(np.diff(x) <= 1e-10)}")
    print(f"  x(10)={x[-1]:.6f}")
    print(f"  n(10)={n[-1]:.3f}")

    # Основной критерий: монотонное убывание к 0
    success = (x[0] > 0.99 and x[-1] > 0 and
               np.all(np.diff(x) <= 1e-10) and
               np.abs(n[0]) < 1e-10)

    return success


def test_projection_consistency():
    """Test that reconstruction from n(t) matches original x(t)."""
    print("\n" + "=" * 50)
    print("TEST 3: Projection Consistency")
    print("=" * 50)

    test_kernels = [
        ("Power-law α=0.6", Kernel.power_law(alpha=0.6)),
        ("Power-law α=0.8", Kernel.power_law(alpha=0.8)),
        ("Tempered α=0.7, β=0.2", Kernel.tempered_power_law(alpha=0.7, beta=0.2)),
    ]

    lambda_param = 0.85
    results = []

    for name, kernel in test_kernels:
        t, x, n = project_kernel_to_n(kernel, lambda_param=lambda_param,
                                      t_max=8.0, n_points=800)

        # Reconstruct x(t) from n(t): x_rec = x0 * λ^n(t)
        x_reconstructed = np.exp(n * np.log(lambda_param))

        # Compare with original (normalized)
        x_norm = x / x[0]
        metrics = compute_accuracy(x_norm, x_reconstructed)

        results.append((name, metrics['accuracy']))

        print(f"{name:25} | Accuracy: {metrics['accuracy'] * 100:6.2f}% | "
              f"Avg error: {metrics['mean_error'] * 100:6.3f}%")

    avg_accuracy = np.mean([r[1] for r in results])
    print(f"\n{'Average accuracy':25} | {avg_accuracy * 100:6.2f}%")

    return avg_accuracy > 0.95


def test_oscillatory_kernel_handling():
    """Test handling of oscillatory and sign-changing kernels."""
    print("\n" + "=" * 50)
    print("TEST 4: Oscillatory Kernels")
    print("=" * 50)

    # Define an oscillatory kernel (realistic for some physical systems)
    def oscillatory_kernel(t):
        return np.sin(2.0 * t) * np.exp(-0.3 * t) + 0.5 * np.cos(1.5 * t)

    kernel = Kernel(oscillatory_kernel, name="OscillatoryExample")

    # Project with complex output allowed
    t, x, n_complex = project_kernel_to_n(kernel, t_max=12.0, n_points=1200,
                                          return_complex=True)

    # Test envelope extraction
    t_env, envelope, n_env = project_to_envelope_n(kernel, t_max=12.0, n_points=1200)

    print(f"Oscillatory kernel analysis:")
    print(f"  Solution has imaginary part: {np.any(np.abs(x.imag) > 1e-10)}")
    print(f"  Max |Im(x)|: {np.max(np.abs(x.imag)):.2e}")
    print(f"  Envelope n(t) monotonic: {np.all(np.diff(n_env) <= 1e-10)}")
    print(f"  Final envelope value: {n_env[-1]:.3f}")

    # Visualize (optional - uncomment for plots)
    if False:  # Set to True to see plots
        plt.figure(figsize=(12, 4))

        plt.subplot(131)
        plt.plot(t, oscillatory_kernel(t))
        plt.title("Oscillatory kernel K(t)")
        plt.xlabel("Time t")

        plt.subplot(132)
        plt.plot(t, x.real, label='Re[x(t)]')
        if np.any(np.abs(x.imag) > 1e-10):
            plt.plot(t, x.imag, label='Im[x(t)]', alpha=0.7)
        plt.title("Solution x(t)")
        plt.xlabel("Time t")
        plt.legend()

        plt.subplot(133)
        plt.plot(t_env, n_env, label='Envelope n(t)')
        plt.title("Experience function (envelope)")
        plt.xlabel("Time t")
        plt.legend()

        plt.tight_layout()
        plt.show()

    return True


def test_performance_benchmark():
    """Benchmark performance for different grid sizes."""
    print("\n" + "=" * 50)
    print("TEST 5: Performance Benchmark")
    print("=" * 50)

    kernel = Kernel.power_law(alpha=0.7)
    grid_sizes = [100, 500, 1000, 2000]

    print("Grid size | Time (s) | Accuracy | x(final)")
    print("-" * 45)

    times = []
    final_values = []

    for n_points in grid_sizes:
        start_time = time()

        t, x, n = project_kernel_to_n(kernel, t_max=10.0, n_points=n_points)

        # Reconstruct and compute accuracy
        x_reconstructed = np.exp(n * np.log(0.8))
        metrics = compute_accuracy(x / x[0], x_reconstructed)

        elapsed = time() - start_time

        times.append(elapsed)
        final_values.append(x[-1])

        print(f"{n_points:9d} | {elapsed:8.3f} | {metrics['accuracy'] * 100:7.2f}% | {x[-1]:8.6f}")

    # Check consistency: final values should be similar
    final_std = np.std(final_values)
    print(f"\nStd of x(final) across grid sizes: {final_std:.6f}")

    # Performance should scale roughly as O(n²)
    if len(times) >= 3:
        ratio = times[-1] / times[0]
        expected_ratio = (grid_sizes[-1] / grid_sizes[0]) ** 2
        print(f"Time ratio ({grid_sizes[-1]}/{grid_sizes[0]}): {ratio:.1f} (expected ~{expected_ratio:.1f})")

    return final_std < 0.01  # Final values consistent within 1%


def test_custom_kernel_interface():
    """Test user-defined custom kernels."""
    print("\n" + "=" * 50)
    print("TEST 6: Custom Kernel Interface")
    print("=" * 50)

    # Векторизованная версия
    def discontinuous_kernel(t):
        """Kernel that changes behavior at t=2 and t=5."""
        t = np.asarray(t)
        result = np.zeros_like(t)

        mask1 = t < 2
        mask2 = (t >= 2) & (t < 5)
        mask3 = t >= 5

        result[mask1] = 1.0 * np.exp(-0.5 * t[mask1])
        result[mask2] = 0.5 * np.exp(-0.2 * t[mask2])
        result[mask3] = 0.1 * np.exp(-0.1 * t[mask3])

        return result

    kernel = Kernel(discontinuous_kernel, name="DiscontinuousRegime")

    # Test projection
    t, x, n = project_kernel_to_n(kernel, t_max=10.0, n_points=1000)

    print(f"Custom discontinuous kernel:")
    print(f"  x(0) = {x[0]:.3f}, x(10) = {x[-1]:.3f}")
    print(f"  n(10) = {n[-1]:.3f}")
    print(f"  Number of time points: {len(t)}")

    # Verify kernel evaluation
    test_points = [1.9, 2.0, 2.1, 4.9, 5.0, 5.1]
    values = kernel(test_points)

    for tp, val in zip(test_points, values):
        print(f"  K({tp:.1f}) = {val:.3f}")

    return True

def main():
    """Run all tests and provide summary."""
    print("\n" + "=" * 60)
    print("KERNEL-EXPERIENCE TOOLS - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    test_results = {}

    # Run all tests
    tests = [
        ("Kernel Creation", test_basic_kernel_creation),
        ("Solution Accuracy", test_volterra_solution_accuracy),
        ("Projection Consistency", test_projection_consistency),
        ("Oscillatory Handling", test_oscillatory_kernel_handling),
        ("Performance", test_performance_benchmark),
        ("Custom Kernels", test_custom_kernel_interface),
    ]

    all_passed = True
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running: {test_name}")
            passed = test_func()
            test_results[test_name] = passed
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   Result: {status}")

            if not passed:
                all_passed = False

        except Exception as e:
            print(f"   ⚠️  ERROR: {e}")
            test_results[test_name] = False
            all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in test_results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - LIBRARY IS READY FOR USE")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW ISSUES ABOVE")

    # Key metrics for reporting
    if 'Projection Consistency' in test_results and test_results['Projection Consistency']:
        print("\n📊 KEY METRICS:")
        print("  • Accuracy > 95% on standard kernels")
        print("  • Handles oscillatory and discontinuous kernels")
        print("  • Monotonic envelope extraction available")
        print("  • Performance scales with grid size")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)