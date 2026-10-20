import streamlit as st

from src import metrics, repository as repo, theme

theme.setup("Hábitos")
st.title("Hábitos")

today = metrics.today_lima()
habits = repo.list_habits(active_only=False, on_date=today)

st.subheader("Hábitos actuales")
st.dataframe(
    habits.rename(columns={
        "name": "Hábito", "unit": "Unidad", "frequency": "Frecuencia",
        "direction": "Meta", "active": "Activo", "target": "Meta vigente",
    }).drop(columns="id"),
    hide_index=True,
)

if not habits.empty:
    st.subheader("Cambiar meta")
    st.caption("Los días anteriores se siguen evaluando con la meta antigua.")
    with st.form("meta"):
        name = st.selectbox("Hábito", habits["name"])
        target = st.number_input("Nueva meta", min_value=0.0, step=0.25)
        since = st.date_input("Vigente desde", value=today)
        if st.form_submit_button("Guardar meta"):
            hid = int(habits.loc[habits["name"] == name, "id"].iloc[0])
            try:
                repo.set_goal(hid, target, since)
                st.success("Meta actualizada")
            except ValueError as e:
                st.error(str(e))

    st.subheader("Activar / desactivar")
    st.caption("Desactivar conserva todo el historial.")
    with st.form("activo"):
        name2 = st.selectbox("Hábito", habits["name"], key="act")
        active = st.checkbox("Activo", value=True)
        if st.form_submit_button("Aplicar"):
            hid = int(habits.loc[habits["name"] == name2, "id"].iloc[0])
            repo.set_active(hid, active)
            st.success("Listo")

st.subheader("Nuevo hábito")
with st.form("nuevo"):
    n = st.text_input("Nombre")
    unit = st.text_input("Unidad (litros, horas, minutos, veces)")
    freq = st.selectbox("Frecuencia", ["daily", "weekly"],
                        format_func=lambda f: "Diario" if f == "daily" else "Semanal (marcas los días que lo haces)")
    direction = st.selectbox("Tipo de meta", ["min", "max"],
                             format_func=lambda d: "Al menos" if d == "min" else "Como máximo")
    goal = st.number_input("Meta (por día, o por semana si es semanal)", min_value=0.0, step=0.25)
    start = st.date_input("Vigente desde", value=today, key="start_new")
    if st.form_submit_button("Crear hábito", type="primary"):
        if not n.strip() or not unit.strip():
            st.error("Nombre y unidad son obligatorios.")
        else:
            try:
                repo.add_habit(n.strip(), unit.strip(), freq, direction, goal, start)
                st.success("Hábito creado")
            except Exception as e:  # nombre duplicado, etc.
                st.error(f"No se pudo crear: {e}")
