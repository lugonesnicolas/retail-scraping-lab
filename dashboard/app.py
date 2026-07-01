from pathlib import Path

import pandas as pd
import streamlit as st

EXPORTS_DIR = Path("data/exports")

st.set_page_config(page_title="Retail Scraping Lab", layout="wide")
st.title("Retail Scraping Lab — Dashboard")


def _latest_export() -> Path | None:
    json_files = sorted(EXPORTS_DIR.glob("products_*.json"))
    return json_files[-1] if json_files else None


export_path = _latest_export()

if export_path is None:
    st.warning(
        "No se encontraron exports en data/exports/. "
        "Corre `make run-demo` para generar datos de ejemplo."
    )
    st.stop()

df = pd.read_json(export_path)
st.caption(f"Datos cargados desde: {export_path}")

col1, col2 = st.columns(2)
col1.metric("Cantidad de productos", len(df))
col2.metric("Precio promedio", f"{df['price'].mean():.2f}" if not df.empty else "N/A")

st.subheader("Disponibilidad")
if not df.empty:
    st.bar_chart(df["availability"].value_counts())

st.subheader("Productos")
st.dataframe(df, use_container_width=True)
