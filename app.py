import streamlit as st
import sys
import os

# Esto permite que las carpetas se vean entre sí
sys.path.append(os.path.join(os.path.dirname(__file__), 'frontend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Importación corregida para quitar la línea amarilla
from frontend.interface import main_interface 

if __name__ == "__main__":
    main_interface()