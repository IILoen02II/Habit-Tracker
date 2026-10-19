from datetime import timedelta

import streamlit as st

from src import charts, metrics, repository as repo

st.set_page_config(page_title="Estadísticas", page_icon="📊")
st.title("📊 Estadísticas")

today = metrics.today_lima()
habits = repo.list_habits(active_only=False, on_date=today)
if habits.empty:
    st.info("Aún no hay hábitos.")
    st.stop()

name = st.selectbox("Hábito", habits["name"])
h = habits[habits["name"] == name].iloc[0]
days = st.radio("Periodo", [30, 90, 365], format_func=lambda d: f"{d} días", horizontal=True)

if h["frequency"] == "daily":
    df = repo.daily_status(since=today - timedelta(days=365))
    df = df[df["habit_id"] == h["id"]]
    if df.empty:
        st.info("Sin registros todavía.")
        st.stop()
    current, best = metrics.streaks(df.loc[df["met"], "log_date"], today)
    pct = metrics.compliance_pct(df, days, today)
    c1, c2, c3 = st.columns(3)
    c1.metric("Racha actual", f"{current} d")
    c2.metric("Mejor racha", f"{best} d")
    c3.metric(f"Cumplimiento {days} d", "—" if pct is None else f"{pct}%")

    window = df[df["log_date"] >= today - timedelta(days=days - 1)]
    st.plotly_chart(charts.calendar_heatmap(df, today))
    if not window.empty:
        st.plotly_chart(charts.value_line(window, h["unit"]))
        st.plotly_chart(charts.weekday_bar(window))
else:
    df = repo.weekly_status()
    df = df[df["habit_id"] == h["id"]]
    if df.empty:
        st.info("Sin registros todavía.")
        st.stop()
    current, best = metrics.streaks(
        df.loc[df["met"], "week_start"], metrics.week_start(today), step=7
    )
    pct = metrics.weekly_compliance_pct(df)
    c1, c2, c3 = st.columns(3)
    c1.metric("Racha actual", f"{current} sem")
    c2.metric("Mejor racha", f"{best} sem")
    c3.metric("Semanas cumplidas", "—" if pct is None else f"{pct}%")
    st.plotly_chart(charts.weekly_bar(df, h["unit"]))
