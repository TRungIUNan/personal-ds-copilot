"""
W01-T05 — Configuration tập trung

MỤC ĐÍCH
--------
Dành một nơi duy nhất cho policy có thể cấu hình của quality tool, đặc biệt là
threshold severity của missing rate. Cách này ngăn threshold bị rải rác trong
từng function.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum
from numbers import Real

from .exceptions import InvalidConfigurationError


class MissingSeverity(StrEnum):
    """Các nhãn có thể có của kết quả policy missing rate."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class MissingSeverityConfig:
    """Policy severity tập trung cho missing rate.

    thresholds sử dụng lower-bound cho các severity:
    - low
    - medium
    - high
    - critical

    Rate bằng 0.0 luôn được phân loại là ``none``.
    """

    thresholds: dict[str, float] = field(default_factory=dict)


DEFAULT_MISSING_SEVERITY_CONFIG = MissingSeverityConfig(
    thresholds={
        "low": 0.0,
        "medium": 0.10,
        "high": 0.30,
        "critical": 0.50,
    }
)


def classify_missing_severity(
    missing_rate: float,
    config: MissingSeverityConfig = DEFAULT_MISSING_SEVERITY_CONFIG,
) -> MissingSeverity:
    """Map missing rate sang severity theo configuration tập trung.

    Boundary mặc định:
    - 0.00           -> none
    - 0.00 < r < .10 -> low
    - .10 <= r < .30 -> medium
    - .30 <= r < .50 -> high
    - .50 <= r <= 1  -> critical
    """

    # 1. Validate missing rate

    if isinstance(missing_rate, bool) or not isinstance(missing_rate, Real):
        raise InvalidConfigurationError(
            "missing_rate must be a real number."
        )

    rate = float(missing_rate)

    if not math.isfinite(rate):
        raise InvalidConfigurationError(
            "missing_rate must be finite."
        )

    if not 0.0 <= rate <= 1.0:
        raise InvalidConfigurationError(
            "missing_rate must be between 0.0 and 1.0."
        )

    # 2. Validate config object

    if not isinstance(config, MissingSeverityConfig):
        raise InvalidConfigurationError(
            "config must be a MissingSeverityConfig."
        )

    required_labels = {
        "low",
        "medium",
        "high",
        "critical",
    }

    if set(config.thresholds) != required_labels:
        raise InvalidConfigurationError(
            "Missing severity configuration must define exactly "
            "low, medium, high, and critical thresholds."
        )

    # 3. Validate threshold values

    for label, value in config.thresholds.items():
        if isinstance(value, bool) or not isinstance(value, Real):
            raise InvalidConfigurationError(
                f"Threshold '{label}' must be a real number."
            )

        numeric_value = float(value)

        if not math.isfinite(numeric_value):
            raise InvalidConfigurationError(
                f"Threshold '{label}' must be finite."
            )

        if not 0.0 <= numeric_value <= 1.0:
            raise InvalidConfigurationError(
                f"Threshold '{label}' must be between 0.0 and 1.0."
            )

    # 4. Convert thresholds

    low = float(config.thresholds["low"])
    medium = float(config.thresholds["medium"])
    high = float(config.thresholds["high"])
    critical = float(config.thresholds["critical"])

    # 5. Validate threshold semantics/order

    if low != 0.0:
        raise InvalidConfigurationError(
            "The low missing-severity threshold must be 0.0."
        )

    if not low < medium < high < critical:
        raise InvalidConfigurationError(
            "Missing severity thresholds must satisfy "
            "low < medium < high < critical."
        )

    # 6. Classification

    if rate == 0.0:
        return MissingSeverity.NONE

    if rate >= critical:
        return MissingSeverity.CRITICAL

    if rate >= high:
        return MissingSeverity.HIGH

    if rate >= medium:
        return MissingSeverity.MEDIUM

    return MissingSeverity.LOW
