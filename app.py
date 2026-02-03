import streamlit as st
import math

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="wide", page_title="Laguneada Golf")

# --- CONFIGURACIÓN DE LA CANCHA (San Andrés GC - Blancas) ---
SLOPE = 128
RATING = 70.6
PAR_CANCHA = 72
DATOS_HOYOS = [
    {"hoyo": 1, "par": 4, "hcp": 3}, {"hoyo": 2, "par": 4, "hcp": 7},
    {"hoyo": 3, "par": 4, "hcp": 11}, {"hoyo": 4, "par": 3, "hcp": 17},
    {"hoyo": 5, "par": 4, "hcp": 9}, {"hoyo": 6, "par": 5, "hcp": 15},
    {"hoyo": 7, "par": 3, "hcp": 13}, {"hoyo": 8, "par": 5, "hcp": 1},
    {"hoyo": 9, "par": 4, "hcp": 5}, {"hoyo": 10, "par": 5, "hcp": 12},
    {"hoyo": 11, "par": 3, "hcp": 18}, {"hoyo": 12, "par": 5, "hcp": 2},
    {"hoyo": 13, "par": 4, "hcp": 8}, {"hoyo": 14, "par": 4, "hcp": 16},
    {"hoyo": 15, "par": 4, "hcp": 4}, {"hoyo": 16, "par": 3, "hcp": 14},
    {"hoyo": 17, "par": 4, "hcp": 6}, {"hoyo": 18, "par": 4, "hcp": 10}
]

# --- INICIALIZACIÓN DE ESTADOS ---
if 'paso' not in st.session_state:
    st.session_state.paso = 0
if 'jugadores' not in st.session_state:
    st.session_state.jugadores = []
if 'scores' not in st.session_state:
    st.session_state.scores = {h["hoyo"]: {} for h in DATOS_HOYOS}

# --- FUNCIONES DE CÁLCULO ---
def calcular_hcp_juego(index):
    return round((index * (SLOPE / 113)) + (RATING - PAR_CANCHA))

# --- PANTALLA 0: ARMADO DE EQUIPO ---
if st.session_state.paso == 0:
    st.title("⛳ Nueva Laguneada")
    num_j = st.radio("Cantidad de jugadores:", [3, 4], index=1, horizontal=True)
    
    temp_jugadores = []
    for i in range(num_j):
        st.markdown(f"**Jugador {i+1}**")
        c1, c2 = st.columns(2)
        nom = c1.text_input(f"Nombre", value=f"J{i+1}", key=f"nom_cfg_{i}")
        idx = c2.number_input(f"Index", min_value=0.0, max_value=54.0, step=0.1, key=f"idx_cfg_{i}")
        hcp_j = calcular_hcp_juego(idx)
        hcp_n = math.floor(hcp_j * 0.85)
        temp_jugadores.append({"nombre": nom, "hcp_neto": hcp_n})

    if st.button("Empezar Vuelta ➡️", use_container_width=True):
        st.session_state.jugadores = temp_jugadores
        st.session_state.num_j_original = num_j
        st.session_state.paso = 1
        st.rerun()

# --- PANTALLAS 1 A 18: CARGA DE GOLPES ---
elif 1 <= st.session_state.paso <= 18:
    h_idx = st.session_state.paso - 1
    h_actual = DATOS_HOYOS[h_idx]
    st.title(f"Hoyo {h_actual['hoyo']} (Par {h_actual['par']})")

    for i, j in enumerate(st.session_state.jugadores):
        val = st.session_state.scores[h_actual['hoyo']].get(i, 0)
        st.session_state.scores[h_actual['hoyo']][i] = st.number_input(
            f"Golpes Gross {j['nombre']}", 
            min_value=0, max_value=15, value=val, key=f"in_{h_actual['hoyo']}_{i}"
        )

    st.divider()
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Anterior", use_container_width=True):
        st.session_state.paso -= 1
        st.rerun()
    txt = "Revisar Planilla 🏁" if st.session_state.paso == 18 else "Siguiente ➡️"
    if col2.button(txt, use_container_width=True):
        st.session_state.paso += 1
        st.rerun()

# --- PANTALLA 19: RESULTADOS Y RUTINA DE BONUS ---
else:
    st.title("🏆 Planilla de Verificación y Bonus")
    
    resumen = []
    total_neto_final = 0
    n_jug = st.session_state.num_j_original

    for h in DATOS_HOYOS:
        gross_scores = []
        netos_hoyo = []
        datos_fila = {"Hoyo": h['hoyo']}
        
        # Procesar cada jugador
        for i, j in enumerate(st.session_state.jugadores):
            g = st.session_state.scores[h['hoyo']].get(i, 0)
            gross_scores.append(g)
            datos_fila[j['nombre']] = g # Mostrar Gross en la tabla
            
            if g > 0:
                # Calcular ventaja hándicap
                v = (j['hcp_neto'] // 18) + (1 if h['hcp'] <= (j['hcp_neto'] % 18) else 0)
                netos_hoyo.append(g - v)

        # RUTINA DE CÁLCULO
        if len(netos_hoyo) >= 2:
            mejores_netos = sorted(netos_hoyo)[:2]
            suma_base_neto = sum(mejores_netos)
            
            # Lógica de Bonus
            suma_gross_equipo = sum(gross_scores)
            par_objetivo_equipo = h['par'] * n_jug
            bonus = 0
            
            # Caso 1: Suma igual al producto (Par del Equipo)
            if suma_gross_equipo == par_objetivo_equipo:
                bonus = 2 if n_jug == 4 else 1
            
            # Caso 2: Suma menor al producto (Bonus adicional)
            elif 0 < suma_gross_equipo < par_objetivo_equipo:
                # Si es menor, se descuenta 1 golpe adicional al bonus base
                bonus_base = 2 if n_jug == 4 else 1
                bonus = bonus_base + 1
            
            neto_final_hoyo = suma_base_neto - bonus
            vs_doble_par = neto_final_hoyo - (h['par'] * 2)
            total_neto_final += vs_doble_par
            
            datos_fila["Vs Doble Par"] = f"{vs_doble_par}" if vs_doble_par < 0 else (f"+{vs_doble_par}" if vs_doble_par > 0 else "E")
            datos_fila["Bonus"] = f"-{bonus}" if bonus > 0 else "-"
        else:
            datos_fila["Vs Doble Par"] = "FALTAN DATOS"
            datos_fila["Bonus"] = "-"

        resumen.append(datos_fila)

    st.table(resumen)

    # Ajuste por equipo de 3 (Regla original)
    if n_jug == 3:
        total_neto_final -= 6
        st.info("Ajuste equipo de 3: -6 golpes aplicados al total.")

    st.header(f"Score Total Neto: {total_neto_final}")

    st.divider()
    col_edit, col_reset = st.columns(2)
    h_edit = col_edit.selectbox("Corregir hoyo:", range(1, 19))
    if col_edit.button("Ir a Corregir"):
        st.session_state.paso = h_edit
        st.rerun()
    
    if col_reset.button("Reiniciar Todo 🔄", use_container_width=True):
        st.session_state.paso = 0
        st.session_state.scores = {h["hoyo"]: {} for h in DATOS_HOYOS}
        st.rerun()