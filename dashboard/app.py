from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import Engine, make_url

from retail_scraping_lab.analytics import queries
from retail_scraping_lab.config.settings import get_settings
from retail_scraping_lab.models.database import get_engine, get_session, get_session_factory

st.set_page_config(page_title="Retail Scraping Lab", layout="wide")
st.title("Retail Scraping Lab — Dashboard")


def _sqlite_db_path(database_url: str) -> Path | None:
    """Ruta del archivo SQLite de `database_url`, o None si no aplica (otro motor, in-memory)."""
    url = make_url(database_url)
    if not url.drivername.startswith("sqlite") or not url.database or url.database == ":memory:":
        return None
    return Path(url.database)


@st.cache_resource
def _get_engine(database_url: str) -> Engine:
    return get_engine(database_url)


settings = get_settings()
db_path = _sqlite_db_path(settings.database_url)

if db_path is not None and not db_path.exists():
    st.warning(f"No se encontro la base de datos en `{db_path}`.")
    st.markdown("Para generarla y cargar datos de ejemplo, corre en la terminal:")
    st.code("make init-db\npython -m retail_scraping_lab.cli scrape-demo --persist")
    st.stop()

engine = _get_engine(settings.database_url)
session_factory = get_session_factory(engine)

with get_session(session_factory) as session:
    total_products = queries.count_products(session)

    if total_products == 0:
        st.info("La base de datos existe pero todavia no tiene productos.")
        st.markdown("Para cargar datos de ejemplo, corre en la terminal:")
        st.code("python -m retail_scraping_lab.cli scrape-demo --persist")
        st.stop()

    st.caption(f"Datos leidos desde: {settings.database_url}. Todas las fechas estan en UTC.")

    st.header("Overview")
    total_snapshots = queries.count_snapshots(session)
    avg_price = queries.average_current_price(session)
    availability = queries.current_availability_breakdown(session)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de productos", total_products)
    col2.metric("Total de snapshots", total_snapshots)
    col3.metric("Precio promedio actual", f"{avg_price:.2f}" if avg_price is not None else "N/A")
    col4.metric(
        "En stock / sin stock / desconocida",
        f"{availability['in_stock']} / {availability['out_of_stock']} / {availability['unknown']}",
    )

    st.header("Latest products")
    latest_rows = queries.latest_snapshots(session)
    latest_df = pd.DataFrame(
        [
            {
                "Fuente": row.source_name,
                "Nombre": row.name,
                "Marca": row.brand,
                "Precio": float(row.price),
                "Moneda": row.currency,
                "Disponibilidad": row.availability,
                "Observado (UTC)": row.scraped_at,
                "URL": row.product_url,
            }
            for row in latest_rows
        ]
    )
    st.dataframe(
        latest_df,
        width="stretch",
        hide_index=True,
        column_config={"URL": st.column_config.LinkColumn("URL")},
    )

    st.header("Price changes")
    st.caption("Productos cuyo precio cambio entre sus dos observaciones mas recientes.")
    changes = queries.price_changes(session)
    if not changes:
        st.info("Ningun producto cambio de precio entre sus dos ultimas observaciones.")
    else:
        changes_df = pd.DataFrame(
            [
                {
                    "Nombre": change.name,
                    "Precio anterior": float(change.previous_price),
                    "Precio actual": float(change.current_price),
                    "Variacion": float(change.change),
                    "Variacion %": round(float(change.change_pct), 2),
                    "Observacion anterior (UTC)": change.previous_scraped_at,
                    "Observacion actual (UTC)": change.current_scraped_at,
                }
                for change in changes
            ]
        )
        st.dataframe(changes_df, width="stretch", hide_index=True)

    st.header("Price history")
    products = queries.list_products(session)
    product_by_name = {product.name: product.id for product in products}
    selected_name = st.selectbox("Producto", options=list(product_by_name.keys()))
    if selected_name:
        history = queries.price_history(session, product_by_name[selected_name])
        history_df = pd.DataFrame(
            {"price": [float(point.price) for point in history]},
            index=[point.scraped_at for point in history],
        )
        if history_df.empty:
            st.info("Este producto todavia no tiene historial de precios.")
        else:
            st.line_chart(history_df)

    st.header("Scrape runs")
    runs = queries.recent_scrape_runs(session)
    runs_df = pd.DataFrame(
        [
            {
                "Fuente": run.source_name,
                "Inicio": run.started_at,
                "Fin": run.finished_at,
                "Estado": run.status,
                "Encontrados": run.products_found,
                "Insertados": run.products_inserted,
                "Actualizados": run.products_updated,
                "Snapshots omitidos": run.snapshots_skipped,
                "Errores": run.errors_count,
            }
            for run in runs
        ]
    )
    if runs_df.empty:
        st.info("Todavia no hay corridas de scraping registradas.")
    else:
        st.dataframe(runs_df, width="stretch", hide_index=True)

    st.header("Errors")
    errors = queries.recent_errors(session)
    if not errors:
        st.info("No hay errores recientes.")
    else:
        errors_df = pd.DataFrame(
            [
                {
                    "Corrida": error.run_id,
                    "Tipo": error.error_type,
                    "Mensaje": error.message,
                    "URL": error.url,
                    "Fecha": error.created_at,
                }
                for error in errors
            ]
        )
        st.dataframe(errors_df, width="stretch", hide_index=True)
