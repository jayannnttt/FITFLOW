"""
Unit tests for PerformanceAnalyzer.
"""
import pytest
from analytics.performance import PerformanceAnalyzer

def test_performance_analysis_perfect_smoothness():
    analyzer = PerformanceAnalyzer()

    # Uniform transitions (completely linear, yielding standard deviation of 0 velocity)
    angle_history = [100.0, 110.0, 120.0, 130.0, 140.0, 150.0]

    analysis = analyzer.analyze_rep(angle_history)

    assert analysis["smoothness"] == 100
    assert analysis["depth"] > 50
    assert analysis["score"] > 50
    assert analysis["warning"] == ""

def test_performance_analysis_uncontrolled_jitter():
    analyzer = PerformanceAnalyzer()

    # Highly erratic angle profile
    angle_history = [100.0, 150.0, 90.0, 160.0, 80.0, 170.0]

    analysis = analyzer.analyze_rep(angle_history)

    # Erratic motion should result in low smoothness score and trigger a warning
    assert analysis["smoothness"] < 60
    assert analysis["warning"] == "Control movement"
