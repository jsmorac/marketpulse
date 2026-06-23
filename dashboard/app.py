"""MarketPulse — dashboard de inteligencia del mercado laboral tech."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from db.connection import connect

st.set_page_config(
    page_title="MarketPulse",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(ttl=600)
def load_demand() -> pd.DataFrame:
    """Trae fct_tech_demand del día más reciente. Cacheado 10 min."""
    query = """
        SELECT technology, tech_group, job_count
        FROM analytics.fct_tech_demand
        WHERE snapshot_date = (
            SELECT max(snapshot_date) FROM analytics.fct_tech_demand
        )
        ORDER BY job_count DESC
    """
    with connect() as conn:
        return pd.read_sql(query, conn)


def main() -> None:
    st.title("📊 MarketPulse")
    st.caption("Inteligencia del mercado laboral tech remoto · Himalayas + RemoteOK")

    df = load_demand()

    if df.empty:
        st.warning("No hay datos todavía. Corre el pipeline de ingesta primero.")
        return

    # Separamos 'other' del resto para los cálculos
    df_tech = df[df["technology"] != "other"].copy()
    total_jobs = int(df["job_count"].sum())
    other_jobs = int(df[df["technology"] == "other"]["job_count"].sum())
    other_pct = (other_jobs / total_jobs * 100) if total_jobs else 0

    # --- Fila de métricas ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Tecnologías rastreadas", len(df_tech))
    col2.metric("Menciones totales", total_jobs)
    col3.metric("Sin clasificar (other)", f"{other_pct:.0f}%")

    st.divider()

    # --- Vista 1: Ranking de tecnologías ---
    st.subheader("Tecnologías más demandadas")
    top = df_tech.head(20)
    fig_rank = px.bar(
        top,
        x="job_count",
        y="technology",
        color="tech_group",
        orientation="h",
        labels={"job_count": "Jobs", "technology": "", "tech_group": "Grupo"},
    )
    fig_rank.update_layout(yaxis={"categoryorder": "total ascending"}, height=600)
    st.plotly_chart(fig_rank, use_container_width=True)

    # --- Vista 2: Demanda por grupo ---
    st.subheader("Demanda por categoría")
    by_group = (
        df_tech.groupby("tech_group", as_index=False)["job_count"]
        .sum()
        .sort_values("job_count", ascending=False)
    )
    fig_group = px.pie(
        by_group,
        values="job_count",
        names="tech_group",
        hole=0.4,
    )
    st.plotly_chart(fig_group, use_container_width=True)

    # --- Vista 3: Cobertura (el termómetro de 'other') ---
    st.subheader("Cobertura del diccionario de tecnologías")
    st.caption(
        "Qué porción de menciones cae en 'other' (no reconocidas por el seed). "
        "Si 'other' crece mucho, conviene revisar qué tecnologías se escapan."
    )
    coverage = pd.DataFrame(
        {
            "tipo": ["Clasificadas", "Sin clasificar (other)"],
            "jobs": [total_jobs - other_jobs, other_jobs],
        }
    )
    fig_cov = px.bar(
        coverage,
        x="jobs",
        y="tipo",
        orientation="h",
        color="tipo",
        color_discrete_map={
            "Clasificadas": "#2563eb",
            "Sin clasificar (other)": "#94a3b8",
        },
    )
    fig_cov.update_layout(showlegend=False, height=200)
    st.plotly_chart(fig_cov, use_container_width=True)


if __name__ == "__main__":
    main()
