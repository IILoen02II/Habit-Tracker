from datetime import timedelta

import streamlit as st

from src import metrics, repository as repo, theme

theme.setup("Habit Tracker")

today = metrics.today_lima()
habits = repo.list_habits(on_date=today)

if habits.empty:
    theme.hero(metrics.format_date_es(today), "Hoy", "No hay hábitos activos todavía.")
    st.page_link("pages/3_Habitos.py", label="Crear un hábito", icon=":material/add:")
    st.stop()

logs = repo.get_logs(today)
week = repo.week_totals(metrics.week_start(today), today)
daily = repo.daily_status(since=today - timedelta(days=365))
weekly = repo.weekly_status()

rows = []
for h in habits.itertuples():
    target = None if h.target != h.target else float(h.target)  # NaN -> None
    if h.frequency == "weekly":
        total = week.get(h.id, 0.0)
        met = None if target is None else total >= target
        goal = f" / {target:g}" if target is not None else ""
        detail = f"Esta semana: {total:g}{goal} {h.unit}"
        progress = min(total / target, 1.0) if target else None
        sub = weekly[weekly["habit_id"] == h.id]
        current, _ = metrics.streaks(
            sub.loc[sub["met"], "week_start"], metrics.week_start(today), step=7
        )
        streak = f"{current} sem"
    else:
        value = logs.get(h.id)
        met = metrics.is_met(value, target, h.direction)
        sign = "≥" if h.direction == "min" else "≤"
        shown = "sin registro" if value is None else f"{value:g} {h.unit}"
        goal = "—" if target is None else f"{sign} {target:g}"
        detail = f"Hoy: {shown} · meta {goal}"
        progress = min(value / target, 1.0) if (h.direction == "min" and target and value is not None) else None
        sub = daily[daily["habit_id"] == h.id]
        current, _ = metrics.streaks(sub.loc[sub["met"], "log_date"], today)
        streak = f"{current} d"
    rows.append(dict(name=h.name, met=met, detail=detail, progress=progress, streak=streak))

done = sum(1 for r in rows if r["met"])
theme.hero(
    metrics.format_date_es(today),
    "Hoy",
    f"{done} de {len(rows)} metas cumplidas",
)

for r in rows:
    with st.container(border=True):
        st.markdown(
            f'<div class="habit"><div>{theme.mark(r["met"])}<b>{r["name"]}</b><br>'
            f'<span class="muted">{r["detail"]}</span></div>'
            f'<div class="streak">{r["streak"]}<small>racha</small></div></div>',
            unsafe_allow_html=True,
        )
        if r["progress"] is not None:
            st.progress(r["progress"])

st.page_link("pages/1_Registro.py", label="Registrar hábitos", icon=":material/edit:")
