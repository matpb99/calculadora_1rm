import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de 1RM", page_icon="💪", layout="centered")

def epley(weight, reps):
    return weight * (1 + 0.0333 * reps)

def brzycki(weight, reps):
    return weight * (36 / (37 - reps))

def lander(weight, reps):
    return (100 * weight) / (101.3 - 2.67123 * reps)

rep_factors = {
    "Press Banca": {1: 1.00, 2: 0.95, 3: 0.93, 4: 0.90, 5: 0.87, 6: 0.85, 7: 0.83, 8: 0.80, 9: 0.77, 10: 0.75},
    "Sentadilla": {1: 1.00, 2: 0.96, 3: 0.94, 4: 0.92, 5: 0.89, 6: 0.86, 7: 0.84, 8: 0.82, 9: 0.79, 10: 0.77},
    "Peso Muerto": {1: 1.00, 2: 0.97, 3: 0.95, 4: 0.93, 5: 0.90, 6: 0.87, 7: 0.85, 8: 0.83, 9: 0.81, 10: 0.79},
    "Dominadas Lastre": {1: 1.00, 2: 0.95, 3: 0.93, 4: 0.90, 5: 0.87, 6: 0.85, 7: 0.83, 8: 0.80, 9: 0.77, 10: 0.75},
    "Fondos Lastre": {1: 1.00, 2: 0.95, 3: 0.93, 4: 0.90, 5: 0.87, 6: 0.85, 7: 0.83, 8: 0.80, 9: 0.77, 10: 0.75}
}

def generar_tabla(estimado_1rm, formula, ejercicio=None):
    data = []
    ejercicio_factor = ejercicio if ejercicio in rep_factors else None

    for reps in range(1, 11):
        if reps == 1:
            peso = estimado_1rm
        else:
            if ejercicio_factor:
                factor = rep_factors[ejercicio_factor].get(reps, 1 / (1 + 0.0333 * reps))
                peso = estimado_1rm * factor
            else:
                if formula == "Epley":
                    peso = estimado_1rm / (1 + 0.0333 * reps)
                elif formula == "Brzycki":
                    peso = estimado_1rm * (37 - reps) / 36
                elif formula == "Lander":
                    peso = (estimado_1rm * (101.3 - 2.67123 * reps)) / 100
        data.append([reps, round(peso, 2)])
    return pd.DataFrame(data, columns=["Reps", f"Peso ({formula})"])


st.title("💪 Calculadora de 1RM (peso máximo a 1 repetición).")
st.markdown("Estima tu **máximo para una repetición (1RM)** y obtén una tabla de pesos y repeticiones.")

with st.container(border=True):
    st.header("🏋️‍♂️ Ingresa tus datos", anchor=False)
    
    ejercicio = st.selectbox(
        "Elige el ejercicio",
        ["Press Banca", "Sentadilla", "Peso Muerto", "Dominadas con lastre", "Fondos con lastre"],
        help="Selecciona el ejercicio que realizaste. Esto ayuda a ajustar los cálculos."
    )

    col1, col2 = st.columns(2)
    
    peso_total = 0
    peso_corporal = 0

    if ejercicio in ["Dominadas con lastre", "Fondos con lastre"]:
        with col1:
            peso_corporal = st.number_input("Tu peso corporal (kg)", min_value=40, step=1, value=70)
        with col2:
            lastre = st.number_input("Lastre añadido (kg)", min_value=5, step=1, value=5)
        peso_total = peso_corporal + lastre
    else:
        with col1:
            peso_total = st.number_input("Peso levantado (kg)", min_value=20, step=1, value=100)

    reps = st.number_input("Repeticiones realizadas", min_value=1, max_value=10, step=1, value=3,
    help="El número de repeticiones completadas.")

if peso_total > 0 and reps > 0:
    st.header("📊 Resultados", anchor=False)

    rm_epley = epley(peso_total, reps)
    rm_brzycki = brzycki(peso_total, reps)
    rm_lander = lander(peso_total, reps)
    
    if ejercicio in ["Dominadas con lastre", "Fondos con lastre"]:
        rm_epley -= peso_corporal
        rm_brzycki -= peso_corporal
        rm_lander -= peso_corporal

    promedio_1rm = (rm_epley + rm_brzycki + rm_lander) / 3

    st.subheader("Estimación de tu 1RM", anchor=False)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⭐ Promedio 1RM", f"{promedio_1rm:.1f} kg", help="El promedio de las tres fórmulas.")
    with col2:
        st.metric("Epley", f"{rm_epley:.1f} kg")
    with col3:
        st.metric("Brzycki", f"{rm_brzycki:.1f} kg")
    with col4:
        st.metric("Lander", f"{rm_lander:.1f} kg")

    df_epley = generar_tabla(rm_epley, "Epley", ejercicio)
    df_brzycki = generar_tabla(rm_brzycki, "Brzycki", ejercicio)
    df_lander = generar_tabla(rm_lander, "Lander", ejercicio)

    df_merge = df_epley.merge(df_brzycki, on="Reps").merge(df_lander, on="Reps")
    df_merge["Promedio"] = df_merge[[f"Peso (Epley)", f"Peso (Brzycki)", f"Peso (Lander)"]].mean(axis=1).round(1)
    
    df_consolidada = df_merge[["Reps", "Promedio"]].rename(columns={"Promedio": "Peso Estimado (kg)"})

    st.subheader("Tabla de Pesos y Repeticiones", anchor=False)

    st.dataframe(df_consolidada, use_container_width=True, hide_index=True)

    with st.expander("Ver tablas de cada fórmula individualmente"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Epley")
            st.dataframe(df_epley, use_container_width=True, hide_index=True)
        with col2:
            st.write("Brzycki")
            st.dataframe(df_brzycki, use_container_width=True, hide_index=True)
        with col3:
            st.write("Lander")
            st.dataframe(df_lander, use_container_width=True, hide_index=True)
else:
    st.info("Ingresa tus datos en el formulario de arriba para calcular tu 1RM.")
