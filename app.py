import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE RUTAS Y SEDE ---
SEDE_ACTUAL = "Sede Centro" 
CARPETA_DATOS = "datos"

# Crear la carpeta de datos si no existe
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

st.set_page_config(page_title=f"Glow & Style - {SEDE_ACTUAL}", page_icon="✨", layout="wide")

# Rutas de archivos dentro de 'datos'
ARCHIVO_PRODUCTOS = os.path.join(CARPETA_DATOS, f"inventario_{SEDE_ACTUAL.replace(' ', '_')}.csv")
ARCHIVO_VENTAS = os.path.join(CARPETA_DATOS, f"ventas_{SEDE_ACTUAL.replace(' ', '_')}.csv")
ARCHIVO_USUARIOS = os.path.join(CARPETA_DATOS, "usuarios_sistema.csv")

# --- 2. FUNCIONES DE BASE DE DATOS ---
def cargar_datos(archivo, columnas):
    if os.path.exists(archivo) and os.stat(archivo).st_size > 0:
        return pd.read_csv(archivo)
    return pd.DataFrame(columns=columnas)

# Inicializar usuarios
if 'users' not in st.session_state:
    df_u = cargar_datos(ARCHIVO_USUARIOS, ["Usuario", "Clave", "Rol", "Nombre"])
    if df_u.empty:
        df_u = pd.DataFrame([{"Usuario": "admin", "Clave": "1234", "Rol": "Dueño", "Nombre": "Anderson"}])
        df_u.to_csv(ARCHIVO_USUARIOS, index=False)
    st.session_state.users = df_u

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. LOGIN ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrar Trabajadora"])
    with tab1:
        u = st.text_input("Usuario", key="login_u")
        p = st.text_input("Contraseña", type="password", key="login_p")
        if st.button("🚀 Ingresar", use_container_width=True):
            user_data = st.session_state.users[st.session_state.users["Usuario"] == u]
            if not user_data.empty and str(user_data.iloc[0]["Clave"]) == p:
                st.session_state.logged_in = True
                st.session_state.user_info = user_data.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    with tab2:
        nu = st.text_input("Nuevo Usuario")
        nn = st.text_input("Nombre Real")
        np = st.text_input("Clave")
        nr = st.selectbox("Rol", ["Vendedora", "Dueño"])
        if st.button("Registrar"):
            nueva = pd.DataFrame([{"Usuario": nu, "Clave": np, "Rol": nr, "Nombre": nn}])
            st.session_state.users = pd.concat([st.session_state.users, nueva], ignore_index=True)
            st.session_state.users.to_csv(ARCHIVO_USUARIOS, index=False)
            st.success("¡Registrada con éxito!")
    st.stop()

# --- 4. INTERFAZ PRINCIPAL ---
user = st.session_state.user_info
st.sidebar.title("✨ Glow & Style")

# Muestra el logo si lo guardaste como logo.png
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)

st.sidebar.info(f"📍 {SEDE_ACTUAL}\n👤 {user['Nombre']}")

menu = ["💸 Realizar Venta", "📦 Ver Inventario"]
if user["Rol"] == "Dueño":
    menu += ["⚙️ Gestionar Productos", "📊 Reporte Maestro"]

choice = st.sidebar.radio("Menú", menu)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.logged_in = False
    st.rerun()

# --- 5. MÓDULOS ---

# Mensaje de éxito persistente
if 'msj_exito' in st.session_state:
    st.success(st.session_state.msj_exito)
    del st.session_state.msj_exito

if choice == "💸 Realizar Venta":
    st.title("💸 Punto de Venta")
    inv = cargar_datos(ARCHIVO_PRODUCTOS, ["ID", "Producto", "Precio", "Stock"])
    if not inv.empty:
        psel = st.selectbox("Producto:", ["---"] + inv["Producto"].tolist())
        if psel != "---":
            d = inv[inv["Producto"] == psel].iloc[0]
            cant = st.number_input("Cantidad", min_value=1, max_value=int(d['Stock']))
            total = cant * d['Precio']
            st.metric("Total", f"${total:,} COP")
            if st.button("Confirmar Venta"):
                inv.loc[inv["Producto"] == psel, "Stock"] -= cant
                inv.to_csv(ARCHIVO_PRODUCTOS, index=False)
                v_df = cargar_datos(ARCHIVO_VENTAS, ["Fecha", "Producto", "Cantidad", "Total", "Vendedora"])
                nv = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m %H:%M"), "Producto": psel, "Cantidad": cant, "Total": total, "Vendedora": user['Nombre']}])
                pd.concat([v_df, nv], ignore_index=True).to_csv(ARCHIVO_VENTAS, index=False)
                st.session_state.msj_exito = f"✅ Venta de {psel} realizada."
                st.rerun()

elif choice == "⚙️ Gestionar Productos":
    st.title("⚙️ Administración")
    inv = cargar_datos(ARCHIVO_PRODUCTOS, ["ID", "Producto", "Precio", "Stock"])
    
    with st.expander("➕ Agregar Nuevo"):
        with st.form("add"):
            n = st.text_input("Nombre")
            p = st.number_input("Precio", min_value=0)
            s = st.number_input("Stock", min_value=0)
            if st.form_submit_button("Guardar"):
                nuevo = pd.DataFrame([{"ID": len(inv)+1, "Producto": n, "Precio": p, "Stock": s}])
                pd.concat([inv, nuevo], ignore_index=True).to_csv(ARCHIVO_PRODUCTOS, index=False)
                st.session_state.msj_exito = f"✨ {n} agregado."
                st.rerun()

    if not inv.empty:
        st.subheader("✏️ Editar Producto")
        p_edit = st.selectbox("Selecciona:", inv["Producto"].tolist())
        idx = inv.index[inv["Producto"] == p_edit][0]
        with st.form("edit"):
            en = st.text_input("Nombre", value=inv.at[idx, "Producto"])
            ep = st.number_input("Precio", value=int(inv.at[idx, "Precio"]))
            es = st.number_input("Stock", value=int(inv.at[idx, "Stock"]))
            if st.form_submit_button("💾 Guardar Cambios"):
                inv.at[idx, "Producto"] = en
                inv.at[idx, "Precio"] = ep
                inv.at[idx, "Stock"] = es
                inv.to_csv(ARCHIVO_PRODUCTOS, index=False)
                st.session_state.msj_exito = f"✅ ¡{en} actualizado!"
                st.rerun()

elif choice == "📦 Ver Inventario":
    st.title("📦 Stock")
    st.dataframe(cargar_datos(ARCHIVO_PRODUCTOS, ["ID", "Producto", "Precio", "Stock"]), use_container_width=True)

elif choice == "📊 Reporte Maestro":
    st.title("📊 Ventas")
    v_df = cargar_datos(ARCHIVO_VENTAS, ["Fecha", "Producto", "Cantidad", "Total", "Vendedora"])
    st.metric("Total Caja", f"${v_df['Total'].sum():,} COP")
    st.dataframe(v_df, use_container_width=True)