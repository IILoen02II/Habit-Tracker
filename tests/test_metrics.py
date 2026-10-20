from datetime import date

import pandas as pd

from src import metrics

D = date


def test_streak_alive_today():
    cur, best = metrics.streaks([D(2026, 10, 13), D(2026, 10, 14), D(2026, 10, 15)], D(2026, 10, 15))
    assert (cur, best) == (3, 3)


def test_streak_alive_if_last_was_yesterday():
    cur, best = metrics.streaks([D(2026, 10, 13), D(2026, 10, 14)], D(2026, 10, 15))
    assert (cur, best) == (2, 2)


def test_streak_broken():
    cur, best = metrics.streaks([D(2026, 10, 1), D(2026, 10, 2), D(2026, 10, 3), D(2026, 10, 10)], D(2026, 10, 15))
    assert (cur, best) == (0, 3)


def test_streak_empty():
    assert metrics.streaks([], D(2026, 10, 15)) == (0, 0)


def test_weekly_streak():
    weeks = [D(2026, 9, 28), D(2026, 10, 5), D(2026, 10, 12)]
    assert metrics.streaks(weeks, metrics.week_start(D(2026, 10, 15)), step=7) == (3, 3)


def test_week_starts_monday():
    assert metrics.week_start(D(2026, 10, 15)) == D(2026, 10, 12)  # jueves -> lunes
    assert metrics.week_start(D(2026, 10, 18)) == D(2026, 10, 12)  # domingo -> lunes


def test_format_date_es():
    assert metrics.format_date_es(D(2026, 10, 19)) == "Lunes 19 de octubre"


def test_is_met():
    assert metrics.is_met(2.0, 2.0, "min") is True or metrics.is_met(2.0, 2.0, "min")
    assert not metrics.is_met(1.5, 2.0, "min")
    assert metrics.is_met(1.0, 2.0, "max")
    assert not metrics.is_met(3.0, 2.0, "max")
    assert metrics.is_met(None, 2.0, "min") is None


def test_compliance_counts_missing_days_as_not_met():
    df = pd.DataFrame({
        "log_date": [D(2026, 10, 13), D(2026, 10, 15)],
        "met": [True, True],
    })
    # ventana desde el primer registro (13) hasta hoy (15) = 3 días, 2 cumplidos
    assert metrics.compliance_pct(df, 30, D(2026, 10, 15)) == 66.7
    assert metrics.compliance_pct(df.iloc[0:0], 30, D(2026, 10, 15)) is None
