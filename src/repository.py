"""Todas las lecturas y escrituras SQL de la app."""
from datetime import date, timedelta

import pandas as pd
from sqlalchemy import text
from src.db import get_engine


def _query(sql: str, **params) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


# ---------------------------------------------------------------- lecturas
def list_habits(active_only: bool = True, on_date: date | None = None) -> pd.DataFrame:
    """Hábitos con la meta vigente en `on_date` (target = NaN si no hay)."""
    on_date = on_date or date.today()
    df = _query(
        """
        SELECT h.id, h.name, h.unit, h.frequency, h.direction, h.active, g.target
        FROM habits h
        LEFT JOIN habit_goals g
               ON g.habit_id = h.id
              AND :d >= g.valid_from
              AND (g.valid_to IS NULL OR :d <= g.valid_to)
        WHERE (NOT :only OR h.active)
        ORDER BY h.id
        """,
        d=on_date,
        only=active_only,
    )
    df["target"] = df["target"].astype(float)
    return df


def get_logs(day: date) -> dict[int, float]:
    df = _query("SELECT habit_id, value FROM daily_logs WHERE log_date = :d", d=day)
    return {int(r.habit_id): float(r.value) for r in df.itertuples()}


def week_totals(start: date, end: date) -> dict[int, float]:
    df = _query(
        """
        SELECT habit_id, SUM(value) AS total
        FROM daily_logs
        WHERE log_date BETWEEN :s AND :e
        GROUP BY habit_id
        """,
        s=start,
        e=end,
    )
    return {int(r.habit_id): float(r.total) for r in df.itertuples()}


def daily_status(since: date) -> pd.DataFrame:
    df = _query(
        """
        SELECT log_date, habit_id, habit, value, target, direction, met
        FROM v_daily_status
        WHERE log_date >= :s
        ORDER BY log_date
        """,
        s=since,
    )
    df["log_date"] = pd.to_datetime(df["log_date"]).dt.date
    df[["value", "target"]] = df[["value", "target"]].astype(float)
    df["met"] = df["met"].astype(bool)
    return df


def weekly_status() -> pd.DataFrame:
    df = _query(
        """
        SELECT week_start, habit_id, habit, total, target, met
        FROM v_weekly_status
        ORDER BY week_start
        """
    )
    df["week_start"] = pd.to_datetime(df["week_start"]).dt.date
    df[["total", "target"]] = df[["total", "target"]].astype(float)
    df["met"] = df["met"].astype(bool)
    return df


# --------------------------------------------------------------- escrituras
def save_logs(day: date, values: dict[int, float]) -> None:
    """Inserta o actualiza el valor de cada hábito para `day`."""
    with get_engine().begin() as conn:
        for habit_id, value in values.items():
            conn.execute(
                text(
                    """
                    INSERT INTO daily_logs (habit_id, log_date, value)
                    VALUES (:h, :d, :v)
                    ON CONFLICT (habit_id, log_date)
                    DO UPDATE SET value = EXCLUDED.value
                    """
                ),
                {"h": habit_id, "d": day, "v": value},
            )


def add_habit(name, unit, frequency, direction, target, valid_from: date) -> None:
    with get_engine().begin() as conn:
        habit_id = conn.execute(
            text(
                """
                INSERT INTO habits (name, unit, frequency, direction)
                VALUES (:n, :u, :f, :d) RETURNING id
                """
            ),
            {"n": name, "u": unit, "f": frequency, "d": direction},
        ).scalar_one()
        conn.execute(
            text(
                "INSERT INTO habit_goals (habit_id, target, valid_from) VALUES (:h, :t, :v)"
            ),
            {"h": habit_id, "t": target, "v": valid_from},
        )


def set_goal(habit_id: int, target: float, valid_from: date) -> None:
    """Cierra la meta vigente el día anterior y abre una nueva desde `valid_from`.

    Los días anteriores siguen evaluándose con la meta antigua.
    """
    with get_engine().begin() as conn:
        cur = conn.execute(
            text(
                "SELECT id, valid_from FROM habit_goals "
                "WHERE habit_id = :h AND valid_to IS NULL"
            ),
            {"h": habit_id},
        ).first()
        if cur is not None:
            if valid_from < cur.valid_from:
                raise ValueError("La fecha debe ser posterior al inicio de la meta vigente.")
            if valid_from == cur.valid_from:
                conn.execute(
                    text("UPDATE habit_goals SET target = :t WHERE id = :i"),
                    {"t": target, "i": cur.id},
                )
                return
            conn.execute(
                text("UPDATE habit_goals SET valid_to = :v WHERE id = :i"),
                {"v": valid_from - timedelta(days=1), "i": cur.id},
            )
        conn.execute(
            text(
                "INSERT INTO habit_goals (habit_id, target, valid_from) VALUES (:h, :t, :v)"
            ),
            {"h": habit_id, "t": target, "v": valid_from},
        )


def set_active(habit_id: int, active: bool) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE habits SET active = :a WHERE id = :i"),
            {"a": active, "i": habit_id},
        )
