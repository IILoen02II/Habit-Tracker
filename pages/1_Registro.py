import streamlit as st

from src import metrics, repository as repo

st.set_page_config(page_title="Registro", page_icon="📝")
st.title("📝 Registro")

STEPS = {"litros": 0.25, "horas": 0.5, "minutos": 5.0}

today = metrics.today_lima()
day = st.date_input("Día (el sueño va en el día en que despiertas)", value=today, max_value=today)

habits = repo.list_habits(on_date=day)
if habits.empty:
    st.info("No hay hábitos activos.")
    st.stop()

saved = repo.get_logs(day)
week = repo.week_totals(metrics.week_start(day), day)
values: dict[int, float] = {}

with st.form("registro"):
    for h in habits.itertuples():
        key = f"h{h.id}_{day}"
        has_goal = h.target == h.target  # False si es NaN
        goal = f"{h.target:g}" if has_goal else "—"
        if h.frequency == "weekly":
            done = st.checkbox(f"{h.name}: lo hice hoy", value=bool(saved.get(h.id, 0)), key=key)
            values[h.id] = 1.0 if done else 0.0
            st.caption(f"Semana: {week.get(h.id, 0):g} / {goal} {h.unit}")
        else:
            sign = "≥" if h.direction == "min" else "≤"
            values[h.id] = st.number_input(
                f"{h.name} ({h.unit})",
                min_value=0.0,
                value=float(saved.get(h.id, 0.0)),
                step=STEPS.get(h.unit, 1.0),
                key=key,
                help=f"Meta: {sign} {goal} {h.unit}",
            )
    submitted = st.form_submit_button("Guardar")

if submitted:
    repo.save_logs(day, values)
    st.success("Guardado ✅")
