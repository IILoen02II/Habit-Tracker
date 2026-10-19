from datetime import timedelta

import streamlit as st

from src import metrics, repository as repo

st.set_page_config(page_title="Habit Tracker", page_icon="✅")
st.title("✅ Hoy")

today = metrics.today_lima()
st.caption(f"{today:%A %d/%m/%Y}")

habits = repo.list_habits(on_date=today)
if habits.empty:
    st.info("No hay hábitos activos. Crea uno en la página Hábitos.")
    st.stop()

logs = repo.get_logs(today)
week = repo.week_totals(metrics.week_start(today), today)
daily = repo.daily_status(since=today - timedelta(days=365))
weekly = repo.weekly_status()

for h in habits.itertuples():
    target = None if h.target != h.target else h.target  # NaN -> None
    with st.container(border=True):
        left, right = st.columns([4, 1])
        if h.frequency == "weekly":
            total = week.get(h.id, 0.0)
            icon = "✅" if target is not None and total >= target else "⏳"
            left.markdown(f"**{icon} {h.name}** · semana: {total:g} / {target:g} {h.unit}"
                          if target is not None else f"**{h.name}** · semana: {total:g} {h.unit}")
            if target:
                left.progress(min(total / target, 1.0))
            sub = weekly[weekly["habit_id"] == h.id]
            current, _ = metrics.streaks(
                sub.loc[sub["met"], "week_start"], metrics.week_start(today), step=7
            )
            right.metric("Racha", f"{current} sem")
        else:
            value = logs.get(h.id)
            met = metrics.is_met(value, target, h.direction)
            icon = "⬜" if met is None else ("✅" if met else "❌")
            sign = "≥" if h.direction == "min" else "≤"
            shown = "sin registro" if value is None else f"{value:g}"
            goal = "—" if target is None else f"{sign} {target:g}"
            left.markdown(f"**{icon} {h.name}** · {shown} {h.unit} (meta {goal})")
            if h.direction == "min" and target and value is not None:
                left.progress(min(value / target, 1.0))
            sub = daily[daily["habit_id"] == h.id]
            current, _ = metrics.streaks(sub.loc[sub["met"], "log_date"], today)
            right.metric("Racha", f"{current} d")

st.page_link("pages/1_Registro.py", label="Registrar hábitos", icon="📝")
