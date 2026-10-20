from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

TZ = ZoneInfo("America/Lima")


def today_lima() -> date:
    return datetime.now(TZ).date()


_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
_MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def format_date_es(d: date) -> str:
    """'Lunes 19 de octubre', sin depender del idioma del sistema."""
    return f"{_DIAS[d.weekday()]} {d.day} de {_MESES[d.month - 1]}"


def week_start(d: date) -> date:
    """Lunes de la semana de `d` (la semana va de lunes a domingo)."""
    return d - timedelta(days=d.weekday())


def is_met(value, target, direction):
    """True/False si se cumple la meta; None si falta el valor o la meta."""
    if value is None or target is None or pd.isna(value) or pd.isna(target):
        return None
    return value >= target if direction == "min" else value <= target


def streaks(dates, reference: date, step: int = 1):
    """Devuelve (racha_actual, mejor_racha).

    dates: fechas cumplidas (días, o lunes de semanas cumplidas con step=7).
    reference: hoy (días) o el lunes de esta semana (semanas).
    La racha actual sigue viva si la última fecha cumplida es la de
    referencia o la anterior.
    """
    days = sorted(set(dates))
    best = run = 0
    prev = None
    for d in days:
        run = run + 1 if prev is not None and (d - prev).days == step else 1
        best = max(best, run)
        prev = d
    current = run if days and (reference - days[-1]).days <= step else 0
    return current, best


def compliance_pct(df: pd.DataFrame, days: int, today: date):
    """% de días cumplidos en los últimos `days` días.

    Cuenta desde el primer registro del hábito; un día sin registro
    cuenta como no cumplido. Devuelve None si no hay datos.
    """
    if df.empty:
        return None
    first = df["log_date"].min()
    start = max(today - timedelta(days=days - 1), first)
    total_days = (today - start).days + 1
    met_days = int(df.loc[df["log_date"] >= start, "met"].astype(bool).sum())
    return round(min(100.0, 100 * met_days / total_days), 1)


def weekly_compliance_pct(df: pd.DataFrame):
    """% de semanas cumplidas (df de v_weekly_status). None si no hay datos."""
    if df.empty:
        return None
    return round(100 * df["met"].astype(bool).mean(), 1)
