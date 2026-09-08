"""Rutas del repositorio, para que cualquier script funcione desde cualquier sitio."""
import os
AQUI    = os.path.dirname(os.path.abspath(__file__))
RAIZ    = os.path.dirname(AQUI)
DATOS   = os.path.join(RAIZ, "datos")
FIGURAS = os.path.join(RAIZ, "figuras")
os.makedirs(DATOS, exist_ok=True); os.makedirs(FIGURAS, exist_ok=True)
def datos(nombre):   return os.path.join(DATOS, nombre)
def figuras(nombre): return os.path.join(FIGURAS, nombre)
