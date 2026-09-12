"""Kiểm thử policy phân loại missing severity của W01-T05."""

import math
from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest

from src.tools.config import (
    DEFAULT_MISSING_SEVERITY_CONFIG,
    MissingSeverity,
    MissingSeverityConfig,
    classify_missing_severity,
)
from src.tools.exceptions import InvalidConfigurationError


def test_default_missing_severity_config_has_expected_thresholds() -> None:
    """Cấu hình mặc định có đúng bốn threshold theo contract."""

    assert DEFAULT_MISSING_SEVERITY_CONFIG.thresholds == {
        "low": 0.0,
        "medium": 0.10,
        "high": 0.30,
        "critical": 0.50,
    }


def test_missing_severity_enum_has_stable_values() -> None:
    """Các label severity có giá trị chuỗi ổn định."""

    assert MissingSeverity.NONE.value == "none"
    assert MissingSeverity.LOW.value == "low"
    assert MissingSeverity.MEDIUM.value == "medium"
    assert MissingSeverity.HIGH.value == "high"
    assert MissingSeverity.CRITICAL.value == "critical"


@pytest.mark.parametrize(
    ("rate", "expected"),
    [
        (0.0, MissingSeverity.NONE),
        (0.01, MissingSeverity.LOW),
        (0.05, MissingSeverity.LOW),
        (0.10, MissingSeverity.MEDIUM),
        (0.20, MissingSeverity.MEDIUM),
        (0.29, MissingSeverity.MEDIUM),
        (0.30, MissingSeverity.HIGH),
        (0.40, MissingSeverity.HIGH),
        (0.49, MissingSeverity.HIGH),
        (0.50, MissingSeverity.CRITICAL),
        (0.75, MissingSeverity.CRITICAL),
        (1.0, MissingSeverity.CRITICAL),
    ],
)
def test_classify_missing_severity_uses_default_policy(
    rate: float,
    expected: MissingSeverity,
) -> None:
    """Rate đại diện được phân loại theo policy mặc định."""

    assert classify_missing_severity(rate) == expected


@pytest.mark.parametrize(
    ("rate", "expected"),
    [
        (0.0, MissingSeverity.NONE),
        (0.10, MissingSeverity.MEDIUM),
        (0.30, MissingSeverity.HIGH),
        (0.50, MissingSeverity.CRITICAL),
        (1.0, MissingSeverity.CRITICAL),
    ],
)
def test_classify_missing_severity_handles_exact_boundaries(
    rate: float,
    expected: MissingSeverity,
) -> None:
    """Các boundary lower-bound được xử lý đúng theo contract."""

    assert classify_missing_severity(rate) == expected


def test_classify_missing_severity_uses_custom_configuration() -> None:
    """Hàm sử dụng threshold từ config tùy chỉnh."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.20,
            "high": 0.40,
            "critical": 0.80,
        }
    )

    assert classify_missing_severity(0.10, config) == MissingSeverity.LOW
    assert classify_missing_severity(0.20, config) == MissingSeverity.MEDIUM
    assert classify_missing_severity(0.50, config) == MissingSeverity.HIGH
    assert classify_missing_severity(0.80, config) == MissingSeverity.CRITICAL


@pytest.mark.parametrize("rate", [None, "0.2", [], {}, True, False])
def test_classify_missing_severity_rejects_non_numeric_or_boolean_rate(
    rate,
) -> None:
    """Rate không phải số thực hoặc là bool phải bị từ chối."""

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(rate)


@pytest.mark.parametrize("rate", [-0.01, -1.0, 1.01, 2.0])
def test_classify_missing_severity_rejects_rate_outside_zero_one_range(
    rate: float,
) -> None:
    """Rate phải nằm trong đoạn từ 0.0 đến 1.0."""

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(rate)


@pytest.mark.parametrize(
    "rate",
    [math.nan, math.inf, -math.inf],
)
def test_classify_missing_severity_rejects_non_finite_rate(rate: float) -> None:
    """Rate NaN hoặc vô cực không phải input hợp lệ."""

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(rate)


def test_classify_missing_severity_rejects_invalid_config_type() -> None:
    """Config phải là một MissingSeverityConfig."""

    invalid_config = cast(Any, {"low": 0.0})

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config=invalid_config)


def test_classify_missing_severity_rejects_missing_threshold_labels() -> None:
    """Config thiếu label threshold phải bị từ chối."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.1,
            "high": 0.3,
        }
    )

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


def test_classify_missing_severity_rejects_extra_threshold_labels() -> None:
    """Config có label ngoài contract phải bị từ chối."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.1,
            "high": 0.3,
            "critical": 0.5,
            "extra": 0.9,
        }
    )

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("medium", "0.1"),
        ("high", True),
        ("critical", None),
    ],
)
def test_classify_missing_severity_rejects_non_numeric_thresholds(
    label: str,
    value,
) -> None:
    """Threshold phải là số thực và không được là bool."""

    thresholds = {
        "low": 0.0,
        "medium": 0.1,
        "high": 0.3,
        "critical": 0.5,
    }
    thresholds[label] = value
    config = MissingSeverityConfig(thresholds=thresholds)

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


@pytest.mark.parametrize(
    "value",
    [math.nan, math.inf, -math.inf],
)
def test_classify_missing_severity_rejects_non_finite_thresholds(
    value: float,
) -> None:
    """Threshold NaN hoặc vô cực phải bị từ chối."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": value,
            "high": 0.3,
            "critical": 0.5,
        }
    )

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


@pytest.mark.parametrize(
    "thresholds",
    [
        {
            "low": 0.0,
            "medium": -0.1,
            "high": 0.3,
            "critical": 0.5,
        },
        {
            "low": 0.0,
            "medium": 0.1,
            "high": 0.3,
            "critical": 1.1,
        },
    ],
)
def test_classify_missing_severity_rejects_thresholds_outside_zero_one_range(
    thresholds: dict,
) -> None:
    """Mọi threshold phải nằm trong đoạn từ 0.0 đến 1.0."""

    config = MissingSeverityConfig(thresholds=thresholds)

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


def test_classify_missing_severity_requires_low_threshold_to_be_zero() -> None:
    """Threshold low phải bắt đầu đúng từ 0.0."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.01,
            "medium": 0.10,
            "high": 0.30,
            "critical": 0.50,
        }
    )

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


@pytest.mark.parametrize(
    "thresholds",
    [
        {
            "low": 0.0,
            "medium": 0.30,
            "high": 0.20,
            "critical": 0.50,
        },
        {
            "low": 0.0,
            "medium": 0.10,
            "high": 0.10,
            "critical": 0.50,
        },
        {
            "low": 0.0,
            "medium": 0.10,
            "high": 0.50,
            "critical": 0.40,
        },
    ],
)
def test_classify_missing_severity_rejects_unordered_or_equal_thresholds(
    thresholds: dict,
) -> None:
    """Threshold phải tăng nghiêm ngặt theo thứ tự severity."""

    config = MissingSeverityConfig(thresholds=thresholds)

    with pytest.raises(InvalidConfigurationError):
        classify_missing_severity(0.2, config)


def test_missing_severity_config_is_frozen() -> None:
    """MissingSeverityConfig không cho phép gán lại thuộc tính."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.1,
            "high": 0.3,
            "critical": 0.5,
        }
    )

    with pytest.raises(FrozenInstanceError):
        # Cố ý thử mutation để kiểm tra frozen configuration.
        config.thresholds = {}  # type: ignore[misc]


def test_classify_missing_severity_does_not_modify_config() -> None:
    """Hàm classify không thay đổi threshold của config tùy chỉnh."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.2,
            "high": 0.4,
            "critical": 0.8,
        }
    )
    before = dict(config.thresholds)

    for rate in [0.0, 0.1, 0.2, 0.5, 0.8, 1.0]:
        classify_missing_severity(rate, config)

    assert config.thresholds == before


def test_classify_missing_severity_is_deterministic() -> None:
    """Cùng rate và config luôn trả về cùng severity."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.2,
            "high": 0.4,
            "critical": 0.8,
        }
    )

    first = classify_missing_severity(0.5, config)
    second = classify_missing_severity(0.5, config)

    assert first == second


def test_classify_missing_severity_does_not_modify_default_config() -> None:
    """Các lần classify không làm thay đổi config mặc định."""

    before = dict(DEFAULT_MISSING_SEVERITY_CONFIG.thresholds)

    for rate in [0.0, 0.01, 0.10, 0.30, 0.50, 1.0]:
        classify_missing_severity(rate)

    assert DEFAULT_MISSING_SEVERITY_CONFIG.thresholds == before
