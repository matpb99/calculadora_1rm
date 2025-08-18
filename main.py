import streamlit as st
import pandas as pd

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
    "Calistenia Lastre": {1: 1.00, 2: 0.95, 3: 0.93, 4: 0.90, 5: 0.87, 6: 0.85, 7: 0.83, 8: 0.80, 9: 0.77, 10: 0.75}
}

def generar_tabla(estimado_1rm, formula, ejercicio=None):
    data = []
    for reps in range(1, 11):
        if reps == 1:
            peso = estimado_1rm 
        else:
            if ejercicio in rep_factors:
                factor = rep_factors[ejercicio].get(reps, 1/(1+0.0333*reps))
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

st.set_page_config(page_title="Calculadora de 1RM",   
    page_icon="💪",
    layout="centered")

st.title("Calculadora de 1RM y tabla de repeticiones")

ejercicio = st.selectbox("Elige el ejercicio", 
                        ["Press Banca", "Sentadilla", "Peso Muerto", "Dominadas con lastre", "Fondos con lastre", "Otro"])

peso_total, peso_lastre = 0, 0

if ejercicio in ["Press Banca", "Sentadilla", "Peso Muerto", "Otro"]:
    peso = st.number_input("Peso levantado (kg)", min_value=20, step=5, value=100)
    peso_total = peso

elif ejercicio in ["Dominadas con lastre", "Fondos con lastre"]:
    peso_corporal = st.number_input("Tu peso corporal (kg)", min_value=50, step=1)
    lastre = st.number_input("Lastre añadido (kg)", min_value=5, step=5)
    peso_total = peso_corporal + lastre
    peso_lastre = lastre

reps = st.number_input("Repeticiones realizadas", min_value=2, max_value=10, step=1)

if peso_total > 0 and reps > 0:
    rm_epley = epley(peso_total, reps)
    rm_brzycki = brzycki(peso_total, reps)
    rm_lander = lander(peso_total, reps)

    if ejercicio in ["Dominadas con lastre", "Fondos con lastre"]:
        rm_epley = epley(peso_total, reps) - peso_corporal
        rm_brzycki = brzycki(peso_total, reps) - peso_corporal
        rm_lander = lander(peso_total, reps) - peso_corporal

    st.subheader("Estimación de 1RM según diferentes fórmulas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Epley", f"{rm_epley:.2f} kg")
    with col2:
        st.metric("Brzycki", f"{rm_brzycki:.2f} kg")
    with col3:
        st.metric("Lander", f"{rm_lander:.2f} kg")

    df_epley = generar_tabla(rm_epley, "Epley", ejercicio)
    df_brzycki = generar_tabla(rm_brzycki, "Brzycki", ejercicio)
    df_lander = generar_tabla(rm_lander, "Lander", ejercicio)

    df_merge = df_epley.merge(df_brzycki, on="Reps").merge(df_lander, on="Reps")
    df_merge["Promedio"] = df_merge[["Peso (Epley)", "Peso (Brzycki)", "Peso (Lander)"]].mean(axis=1).round(2)
    df_consolidada = df_merge[["Reps", "Promedio"]]

    st.subheader("Tabla consolidada de repeticiones y pesos")
    st.dataframe(df_consolidada, use_container_width=True, hide_index=True)

    with st.expander("Ver tablas individuales (Epley, Brzycki, Lander)", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("### Epley")
            st.dataframe(df_epley, use_container_width=True, hide_index=True)

        with col2:
            st.write("### Brzycki")
            st.dataframe(df_brzycki, use_container_width=True, hide_index=True)

        with col3:
            st.write("### Lander")
            st.dataframe(df_lander, use_container_width=True, hide_index=True)