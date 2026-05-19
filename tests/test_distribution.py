"""
tests/test_distribution.py
--------------------------
Property-based tests untuk modules/distribution.py menggunakan Hypothesis.

Properties yang diuji:
- Property 21: MLE for Normal equals numpy mean and std   (Validates: Requirements 6.4)
- Property 22: MLE for Poisson equals sample mean         (Validates: Requirements 6.6)
- Property 23: MLE for Exponential equals reciprocal of mean (Validates: Requirements 6.7)
- Property 24: MLE for Uniform equals (min, max)          (Validates: Requirements 6.8)
"""

import numpy as np
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from modules.distribution import (
    mle_normal,
    mle_poisson,
    mle_exponential,
    mle_uniform,
)

# ---------------------------------------------------------------------------
# Strategi / Generator
# ---------------------------------------------------------------------------

# Nilai float terbatas, tidak NaN/Inf — untuk distribusi Normal dan Uniform
finite_floats = st.floats(
    min_value=-1e6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Nilai float positif — untuk distribusi Exponential (x > 0)
positive_floats = st.floats(
    min_value=1e-6,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Nilai float non-negatif — untuk distribusi Poisson (x >= 0)
non_negative_floats = st.floats(
    min_value=0.0,
    max_value=1e6,
    allow_nan=False,
    allow_infinity=False,
)

# Ukuran array: minimal 2 elemen
array_size = st.integers(min_value=2, max_value=200)


def finite_array_strategy(size: int):
    """Array float terbatas shape (size,) untuk Normal/Uniform."""
    return arrays(
        dtype=np.float64,
        shape=(size,),
        elements=finite_floats,
    )


def positive_array_strategy(size: int):
    """Array float positif shape (size,) untuk Exponential."""
    return arrays(
        dtype=np.float64,
        shape=(size,),
        elements=positive_floats,
    )


def non_negative_array_strategy(size: int):
    """Array float non-negatif shape (size,) untuk Poisson."""
    return arrays(
        dtype=np.float64,
        shape=(size,),
        elements=non_negative_floats,
    )


# ---------------------------------------------------------------------------
# Property 21: MLE for Normal equals numpy mean and std
# Validates: Requirements 6.4
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(array_size.flatmap(finite_array_strategy))
def test_property_21_mle_normal_equals_numpy_mean_std(x):
    """
    **Validates: Requirements 6.4**

    Property 21: Untuk sembarang array float x dengan panjang >= 2,
    mle_normal(x) harus mengembalikan (np.mean(x), np.std(x, ddof=0)).
    """
    assume(np.isfinite(x).all() and len(x) >= 2)

    mu_hat, sigma_hat = mle_normal(x)

    expected_mu = float(np.mean(x))
    expected_sigma = float(np.std(x, ddof=0))

    assert isinstance(mu_hat, float), (
        f"mu_hat harus bertipe float, dapat {type(mu_hat)}"
    )
    assert isinstance(sigma_hat, float), (
        f"sigma_hat harus bertipe float, dapat {type(sigma_hat)}"
    )

    np.testing.assert_allclose(
        mu_hat, expected_mu, rtol=1e-10, atol=1e-10,
        err_msg=f"mle_normal mu harus sama dengan np.mean(x): "
                f"expected {expected_mu}, got {mu_hat}"
    )
    np.testing.assert_allclose(
        sigma_hat, expected_sigma, rtol=1e-10, atol=1e-10,
        err_msg=f"mle_normal sigma harus sama dengan np.std(x, ddof=0): "
                f"expected {expected_sigma}, got {sigma_hat}"
    )


# ---------------------------------------------------------------------------
# Property 22: MLE for Poisson equals sample mean
# Validates: Requirements 6.6
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(array_size.flatmap(non_negative_array_strategy))
def test_property_22_mle_poisson_equals_sample_mean(x):
    """
    **Validates: Requirements 6.6**

    Property 22: Untuk sembarang array float non-negatif x,
    mle_poisson(x) harus mengembalikan np.mean(x).
    """
    assume(np.isfinite(x).all() and len(x) >= 2)

    lambda_hat = mle_poisson(x)

    expected = float(np.mean(x))

    assert isinstance(lambda_hat, float), (
        f"lambda_hat harus bertipe float, dapat {type(lambda_hat)}"
    )
    np.testing.assert_allclose(
        lambda_hat, expected, rtol=1e-10, atol=1e-10,
        err_msg=f"mle_poisson harus sama dengan np.mean(x): "
                f"expected {expected}, got {lambda_hat}"
    )


# ---------------------------------------------------------------------------
# Property 23: MLE for Exponential equals reciprocal of mean
# Validates: Requirements 6.7
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(array_size.flatmap(positive_array_strategy))
def test_property_23_mle_exponential_equals_reciprocal_of_mean(x):
    """
    **Validates: Requirements 6.7**

    Property 23: Untuk sembarang array float positif x,
    mle_exponential(x) harus mengembalikan 1.0 / np.mean(x).
    """
    assume(np.isfinite(x).all() and len(x) >= 2)
    assume(np.mean(x) > 0)  # pastikan mean positif agar 1/mean terdefinisi

    lambda_hat = mle_exponential(x)

    expected = float(1.0 / np.mean(x))

    assert isinstance(lambda_hat, float), (
        f"lambda_hat harus bertipe float, dapat {type(lambda_hat)}"
    )
    np.testing.assert_allclose(
        lambda_hat, expected, rtol=1e-10, atol=1e-10,
        err_msg=f"mle_exponential harus sama dengan 1.0 / np.mean(x): "
                f"expected {expected}, got {lambda_hat}"
    )


# ---------------------------------------------------------------------------
# Property 24: MLE for Uniform equals (min, max)
# Validates: Requirements 6.8
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(array_size.flatmap(finite_array_strategy))
def test_property_24_mle_uniform_equals_min_max(x):
    """
    **Validates: Requirements 6.8**

    Property 24: Untuk sembarang array float x,
    mle_uniform(x) harus mengembalikan (np.min(x), np.max(x)).
    """
    assume(np.isfinite(x).all() and len(x) >= 2)

    a_hat, b_hat = mle_uniform(x)

    expected_a = float(np.min(x))
    expected_b = float(np.max(x))

    assert isinstance(a_hat, float), (
        f"a_hat harus bertipe float, dapat {type(a_hat)}"
    )
    assert isinstance(b_hat, float), (
        f"b_hat harus bertipe float, dapat {type(b_hat)}"
    )

    np.testing.assert_allclose(
        a_hat, expected_a, rtol=1e-10, atol=1e-10,
        err_msg=f"mle_uniform a harus sama dengan np.min(x): "
                f"expected {expected_a}, got {a_hat}"
    )
    np.testing.assert_allclose(
        b_hat, expected_b, rtol=1e-10, atol=1e-10,
        err_msg=f"mle_uniform b harus sama dengan np.max(x): "
                f"expected {expected_b}, got {b_hat}"
    )


# ---------------------------------------------------------------------------
# Unit tests tambahan — verifikasi contoh konkret
# ---------------------------------------------------------------------------

class TestMleNormalConcrete:
    """Unit tests dengan contoh konkret untuk mle_normal."""

    def test_known_values(self):
        """Verifikasi dengan data yang diketahui hasilnya."""
        x = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        mu, sigma = mle_normal(x)
        assert abs(mu - 5.0) < 1e-10, f"mu harus 5.0, dapat {mu}"
        assert abs(sigma - 2.0) < 1e-10, f"sigma harus 2.0, dapat {sigma}"

    def test_constant_array(self):
        """Array konstan: mu = nilai konstan, sigma = 0."""
        x = np.array([3.0, 3.0, 3.0, 3.0])
        mu, sigma = mle_normal(x)
        assert abs(mu - 3.0) < 1e-10
        assert abs(sigma - 0.0) < 1e-10

    def test_two_elements(self):
        """Array dengan 2 elemen."""
        x = np.array([1.0, 3.0])
        mu, sigma = mle_normal(x)
        assert abs(mu - 2.0) < 1e-10
        assert abs(sigma - 1.0) < 1e-10


class TestMlePoissonConcrete:
    """Unit tests dengan contoh konkret untuk mle_poisson."""

    def test_known_values(self):
        x = np.array([1.0, 2.0, 3.0, 4.0])
        lambda_hat = mle_poisson(x)
        assert abs(lambda_hat - 2.5) < 1e-10

    def test_all_zeros(self):
        x = np.array([0.0, 0.0, 0.0])
        lambda_hat = mle_poisson(x)
        assert abs(lambda_hat - 0.0) < 1e-10


class TestMleExponentialConcrete:
    """Unit tests dengan contoh konkret untuk mle_exponential."""

    def test_known_values(self):
        """Jika mean = 2.0, maka lambda = 0.5."""
        x = np.array([1.0, 2.0, 3.0])
        lambda_hat = mle_exponential(x)
        assert abs(lambda_hat - 0.5) < 1e-10

    def test_unit_mean(self):
        """Jika mean = 1.0, maka lambda = 1.0."""
        x = np.array([0.5, 1.0, 1.5])
        lambda_hat = mle_exponential(x)
        assert abs(lambda_hat - 1.0) < 1e-10


class TestMleUniformConcrete:
    """Unit tests dengan contoh konkret untuk mle_uniform."""

    def test_known_values(self):
        x = np.array([2.0, 5.0, 3.0, 7.0, 1.0])
        a, b = mle_uniform(x)
        assert abs(a - 1.0) < 1e-10
        assert abs(b - 7.0) < 1e-10

    def test_sorted_array(self):
        """Array terurut: a = elemen pertama, b = elemen terakhir."""
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        a, b = mle_uniform(x)
        assert abs(a - 0.0) < 1e-10
        assert abs(b - 4.0) < 1e-10

    def test_two_elements(self):
        x = np.array([3.0, 8.0])
        a, b = mle_uniform(x)
        assert abs(a - 3.0) < 1e-10
        assert abs(b - 8.0) < 1e-10
