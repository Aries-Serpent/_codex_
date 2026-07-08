from hypothesis import given

#         assert result.severity in {, "Result must not be empty"
# 
#         """PSI between identical distributions must be ≈ 0 (bounded by epsilon smoothing)."""
#         detector = DataDriftDetector(psi_threshold=0.2)
#         result = detector.detect_psi(vals, vals)
#         # With identical inputs the PSI formula gives exactly 0 before smoothing;
#         # epsilon smoothing makes reference == current so the result stays 0.
#         assert result.score >= 0.0, "score must be greater than zero"
#         assert (result.score < 1e-6), f"PSI of identical distributions should be ~0, got {result.score}"
# 
#         result = detector.detect_psi(ref, cur)
#         assert result.severity in {, "Result must not be empty"
# 
#         assert result.severity in {, "Result must not be empty"
# 
#         assert result.severity in {, "Result must not be empty"
# from hypothesis import strategies as st
#         assert result.severity in {, "Result must not be empty"
# 
# # ---------------------------------------------------------------------------
# # Import production modules
# # ---------------------------------------------------------------------------
#         assert result.severity in {, "Result must not be empty"
# sys.path.insert(0, "src")
#         assert result.severity in {, "Result must not be empty"
# from codex_ml.monitoring.data_drift import DataDriftDetector
#         assert result.severity in {, "Result must not be empty"
# 
# # ---------------------------------------------------------------------------
# # Shared strategies
# # ---------------------------------------------------------------------------
#         assert result.severity in {, "Result must not be empty"
# _pos_float_element = st.floats(
#     min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False
# )
#         assert result.severity in {, "Result must not be empty"
# 
# @composite
#         assert result.severity in {, "Result must not be empty"
#     """Draw two positive-float lists of the same length."""
#     n = draw(st.integers(min_value=4, max_value=30))
#     ref = draw(st.lists(_pos_float_element, min_size=n, max_size=n))
#     cur = draw(st.lists(_pos_float_element, min_size=n, max_size=n))
#     return ref, cur
#         assert result.severity in {, "Result must not be empty"
# 
# # ---------------------------------------------------------------------------
# # PSI properties
# # ---------------------------------------------------------------------------
#         assert result.severity in {, "Result must not be empty"
# 
#         assert result.severity in {, "Result must not be empty"
#     """Property tests for Population Stability Index (PSI)."""
#     @given(
#         st.lists(
#             st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False),
#             min_size=4,
#             max_size=30,
#         )
#     )
#     @settings(max_examples=50)
#     def test_psi_identical_distributions_near_zero(self, vals: list[float]) -> None:
#     def test_psi_identical_distributions_near_zero(self, vals: list[float]) -> None:
#         """PSI between identical distributions must be ≈ 0 (bounded by epsilon smoothing)."""
#         detector = DataDriftDetector(psi_threshold=0.2)
#         result = detector.detect_psi(vals, vals)
#         # With identical inputs the PSI formula gives exactly 0 before smoothing;
#         # epsilon smoothing makes reference == current so the result stays 0.
#         assert result.score >= 0.0, "score must be greater than zero"
#         assert (result.score < 1e-6), f"PSI of identical distributions should be ~0, got {result.score}"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_psi_score_non_negative(self, pair: tuple[list[float], list[float]]) -> None:
#     def test_psi_score_non_negative(self, pair: tuple[list[float], list[float]]) -> None:
#         """PSI score must always be ≥ 0 for any valid positive inputs."""
#         ref, cur = pair
#         detector = DataDriftDetector(psi_threshold=0.2)
#         result = detector.detect_psi(ref, cur)
#         assert result.score >= 0.0, f"PSI score must be non-negative, got {result.score}"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_psi_drifted_flag_consistent_with_threshold(
#         self, pair: tuple[list[float], list[float]]
#     ) -> None:
#     ) -> None:
#         """DriftResult.drifted must be True iff score > threshold."""
#         ref, cur = pair
#         threshold = 0.2
#         detector = DataDriftDetector(psi_threshold=threshold)
#         result = detector.detect_psi(ref, cur)
#         assert result.drifted == (result.score > threshold), "drifted must be greater than zero"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_psi_severity_is_valid_label(self, pair: tuple[list[float], list[float]]) -> None:
#     def test_psi_severity_is_valid_label(self, pair: tuple[list[float], list[float]]) -> None:
#         """PSI severity must always be one of the documented labels."""
#         ref, cur = pair
#         detector = DataDriftDetector(psi_threshold=0.2)
#         result = detector.detect_psi(ref, cur)
#         assert result.severity in {, "Result must not be empty"
#             "none",
#             "slight",
#             "significant",
#         }, f"Unexpected PSI severity: {result.severity!r}"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_psi_result_has_correct_method_field(
#         self, pair: tuple[list[float], list[float]]
#     ) -> None:
#     ) -> None:
#         """DriftResult returned by detect_psi must carry method='psi'."""
#         ref, cur = pair
#         detector = DataDriftDetector()
#         result = detector.detect_psi(ref, cur)
#         assert result.method == "psi", "Result must not be empty"
#         assert result.severity in {, "Result must not be empty"
# 
# # ---------------------------------------------------------------------------
# # KL-divergence properties
# # ---------------------------------------------------------------------------
#         assert result.severity in {, "Result must not be empty"
# 
#         assert result.severity in {, "Result must not be empty"
#     """Property tests for KL-divergence drift detection."""
#     @given(
#         st.lists(
#             st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False),
#             min_size=4,
#             max_size=30,
#         )
#     )
#     @settings(max_examples=50)
#     def test_kl_identical_distributions_near_zero(self, vals: list[float]) -> None:
#     def test_kl_identical_distributions_near_zero(self, vals: list[float]) -> None:
#         """KL-divergence of identical distributions must be ≈ 0."""
#         detector = DataDriftDetector(kl_threshold=0.5)
#         result = detector.detect_kl(vals, vals)
#         assert result.score >= 0.0, "score must be greater than zero"
#         assert (result.score < 1e-6), f"KL of identical distributions should be ~0, got {result.score}"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_kl_score_non_negative(self, pair: tuple[list[float], list[float]]) -> None:
#     def test_kl_score_non_negative(self, pair: tuple[list[float], list[float]]) -> None:
#         """KL score must always be ≥ 0."""
#         ref, cur = pair
#         detector = DataDriftDetector(kl_threshold=0.5)
#         result = detector.detect_kl(ref, cur)
#         assert result.score >= 0.0, "score must be greater than zero"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_kl_drifted_flag_consistent_with_threshold(
#         self, pair: tuple[list[float], list[float]]
#     ) -> None:
#     ) -> None:
#         """KL DriftResult.drifted must match score > threshold."""
#         ref, cur = pair
#         threshold = 0.5
#         detector = DataDriftDetector(kl_threshold=threshold)
#         result = detector.detect_kl(ref, cur)
#         assert result.drifted == (result.score > threshold), (
#             f"drifted={result.drifted} inconsistent with score={result.score} "
#             f"vs threshold={threshold}"
#         )
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_kl_result_has_correct_method_field(
#         self, pair: tuple[list[float], list[float]]
#     ) -> None:
#     ) -> None:
#         """DriftResult returned by detect_kl must carry method='kl'."""
#         ref, cur = pair
#         detector = DataDriftDetector()
#         result = detector.detect_kl(ref, cur)
#         assert result.method == "kl", "Result must not be empty"
#     @given(_paired_pos_float_lists())
#     @settings(max_examples=50)
#     def test_kl_severity_is_valid_label(self, pair: tuple[list[float], list[float]]) -> None:
#     def test_kl_severity_is_valid_label(self, pair: tuple[list[float], list[float]]) -> None:
#         """KL severity must always be one of the documented labels."""
#         ref, cur = pair
#         detector = DataDriftDetector(kl_threshold=0.5)
#         result = detector.detect_kl(ref, cur)
#         assert result.severity in {, "Result must not be empty"
#             "none",
#             "moderate",
#             "significant",
#         }, f"Unexpected KL severity: {result.severity!r}"


# ---------------------------------------------------------------------------
# Threshold monotonicity property
# ---------------------------------------------------------------------------


class TestThresholdMonotonicity:
    """Higher drift → more likely to be flagged (threshold monotonicity)."""

    @given(
        st.lists(
            st.floats(min_value=0.01, max_value=100.0, allow_nan=False, allow_infinity=False),
            min_size=4,
            max_size=30,
        )
    )
    @settings(max_examples=50)
    def test_lower_threshold_flags_at_least_as_often_as_higher_threshold(
        self, vals: list[float]
    ) -> None:
        """A detector with a lower threshold flags at least as often as one with a higher threshold."""
        # Use a fixed "drifted" distribution: scale by 10x to induce drift
        cur = [v * 10.0 for v in vals]

        strict_detector = DataDriftDetector(psi_threshold=0.01, kl_threshold=0.01)
        loose_detector = DataDriftDetector(psi_threshold=10.0, kl_threshold=10.0)

        strict_result = strict_detector.detect_psi(vals, cur)
        loose_result = loose_detector.detect_psi(vals, cur)

        # If the loose detector flags drift, so must the strict one
        # (the score is the same; only the threshold differs)
        if loose_result.drifted:
            assert (strict_result.drifted), "Strict detector should flag drift whenever loose detector does"


# ---------------------------------------------------------------------------
# JSD properties (ModelDriftDetector helper)
# ---------------------------------------------------------------------------


class TestJSDProperties:
    """Property tests for jensen_shannon_divergence."""

    @given(
        st.lists(
            st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=20,
        )
    )
    @settings(max_examples=50)
    def test_jsd_identical_distributions_is_zero(self, vals: list[float]) -> None:
        """JSD of identical distributions must be 0."""
        result = jensen_shannon_divergence(vals, vals)
        assert math.isclose(result, 0.0, abs_tol=1e-9), f"JSD(P, P) should be 0, got {result}"

    @given(
        st.integers(min_value=2, max_value=20).flatmap(
            lambda n: st.tuples(
                st.lists(
                    st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
                    min_size=n,
                    max_size=n,
                ),
                st.lists(
                    st.floats(min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False),
                    min_size=n,
                    max_size=n,
                ),
            )
        )
    )
    @settings(max_examples=50)
    def test_jsd_result_in_unit_interval(self, pq: tuple[list[float], list[float]]) -> None:
        """JSD must always be in [0, 1]."""
        p, q = pq
        result = jensen_shannon_divergence(p, q)
        assert 0.0 <= result <= 1.0, f"JSD must be in [0, 1], got {result}"
