import streamlit as st
import pandas as pd
from datetime import datetime
import os
from backend.logica import cargar_datos, guardar_datos
def main_interface():
    SEDE_ACTUAL = "Sede Centro"
    ARCHIVO_PRODUCTOS = f"inventario_{SEDE_ACTUAL.replace(' ', '_')}.csv"
    ARCHIVO_VENTAS = f"ventas_{SEDE_ACTUAL.replace(' ', '_')}.csv"
    ARCHIVO_USUARIOS = "usuarios_sistema.csv"

    # --- INICIALIZAR USUARIOS ---
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    df_u = cargar_datos(ARCHIVO_USUARIOS, ["Usuario", "Clave", "Rol", "Nombre"])
    if df_u.empty:
        df_u = pd.DataFrame([{"Usuario": "admin", "Clave": "1234", "Rol": "Dueño", "Nombre": "Anderson"}])
        guardar_datos(df_u, ARCHIVO_USUARIOS)

    # --- LOGIN ---
    if not st.session_state.logged_in:
        st.title("✨ Glow & Style - Acceso")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("🚀 Ingresar"):
            user_data = df_u[df_u["Usuario"] == u]
            if not user_data.empty and str(user_data.iloc[0]["Clave"]) == p:
                st.session_state.logged_in = True
                st.session_state.user_info = user_data.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        st.stop()

    # --- INTERFAZ PRINCIPAL ---
    user = st.session_state.user_info
    st.sidebar.title("✨ Glow & Style")
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    st.sidebar.info(f"📍 {SEDE_ACTUAL}\n👤 {user['Nombre']}")

    menu = ["💸 Realizar Venta", "📦 Ver Inventario"]
    if user["Rol"] == "Dueño":
        menu += ["⚙️ Gestionar Productos", "📊 Reporte Maestro"]
    
    choice = st.sidebar.radio("Menú", menu)

    if choice == "💸 Realizar Venta":
        st.title("💸 Punto de Venta")
        inv = cargar_datos(ARCHIVO_PRODUCTOS, ["ID", "Producto", "Precio", "Stock"])
        if not inv.empty:
            psel = st.selectbox("Seleccione Producto:", ["---"] + inv["Producto"].tolist())
            if psel != "---":
                d = inv[inv["Producto"] == psel].iloc[0]
                cant = st.number_input("Cantidad", min_value=1, max_value=int(d['Stock']))
                total = cant * d['Precio']
                st.metric("Total a Cobrar", f"${total:,} COP")
                if st.button("Confirmar Venta"):
                    inv.loc[inv["Producto"] == psel, "Stock"] -= cant
                    guardar_datos(inv, ARCHIVO_PRODUCTOS)
                    v_df = cargar_datos(ARCHIVO_VENTAS, ["Fecha", "Producto", "Cantidad", "Total", "Vendedora"])
                    nv = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m %H:%M"), "Producto": psel, "Cantidad": cant, "Total": total, "Vendedora": user['Nombre']}])
                    guardar_datos(pd.concat([v_df, nv], ignore_index=True), ARCHIVO_VENTAS)
                    st.success("Venta Guardada con éxito")

    elif choice == "📊 Reporte Maestro":
        st.title("📊 Historial de Ventas")
        v_df = cargar_datos(ARCHIVO_VENTAS, ["Fecha", "Producto", "Cantidad", "Total", "Vendedora"])
        st.metric("Total en Caja", f"${v_df['Total'].sum():,} COP")
        st.dataframe(v_df, use_container_width=True)
        csv = v_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte (Excel/CSV)", data=csv, file_name=f"ventas_{SEDE_ACTUAL}.csv", mime='text/csv')

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()