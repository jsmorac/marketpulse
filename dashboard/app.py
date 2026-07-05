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

st.markdown(
    """
    <style>
    h1, h2, h3 {
        font-family: Georgia, 'Times New Roman', serif !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricValue"] { font-family: Georgia, 'Times New Roman', serif; }
    [data-testid="stMetricLabel"] p {
        text-transform: uppercase; letter-spacing: 0.05em;
        font-size: 11px !important; color: #999999 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

GROUP_COLORS = {
    "language": "#D85A30",
    "framework": "#7F77DD",
    "ml": "#EF9F27",
    "data_eng": "#1D9E75",
    "database": "#D4537E",
    "cloud": "#378ADD",
    "devops": "#0F6E56",
    "role_discipline": "#B4B2A9",
    "domain": "#888780",
    "other": "#D3D1C7",
}

PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#3D3929"},
    "margin": {"t": 10, "b": 10, "l": 10, "r": 10},
}


@st.cache_data(ttl=600)
def load_demand_today() -> pd.DataFrame:
    """Snapshot del día más reciente."""
    query = """
        SELECT technology, tech_group, kind, job_count
        FROM analytics.fct_tech_demand
        WHERE snapshot_date = (
            SELECT max(snapshot_date) FROM analytics.fct_tech_demand
        )
        ORDER BY job_count DESC
    """
    with connect() as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_demand_cumulative() -> pd.DataFrame:
    """Demanda acumulada: cada oferta cuenta una sola vez en toda su historia."""
    query = """
        SELECT technology, tech_group, kind, job_count, first_seen, last_seen
        FROM analytics.fct_tech_demand_cumulative
        ORDER BY job_count DESC
    """
    with connect() as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_pipeline_status() -> pd.DataFrame:
    query = """
        SELECT source, max(loaded_at) AS last_load, count(DISTINCT snapshot_date) AS snapshots
        FROM (
            SELECT source, loaded_at, snapshot_date FROM raw.himalayas_jobs
            UNION ALL
            SELECT source, loaded_at, snapshot_date FROM raw.remoteok_jobs
            UNION ALL
            SELECT source, loaded_at, snapshot_date FROM raw.hackernews_jobs
        ) t
        GROUP BY source
        ORDER BY source
    """
    with connect() as conn:
        return pd.read_sql(query, conn)


ACCENT = "#990F3D"
NEUTRAL_BAR = "#D4D4D4"
TRACK = "#F5F5F5"

PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#0A0A0A"},
    "margin": {"t": 10, "b": 10, "l": 10, "r": 40},
}


BLUE_RAMP = [
    "#185FA5",
    "#2E74B8",
    "#378ADD",
    "#5DA0E6",
    "#85B7EB",
    "#A8CAF0",
    "#B5D4F4",
    "#CFE3F8",
    "#E6F1FB",
]


def _gradient_colors(n: int) -> list[str]:
    """Un color por barra, de más saturado (rango #1) a más claro (últimos)."""
    if n <= 1:
        return [BLUE_RAMP[0]]
    step = (len(BLUE_RAMP) - 1) / (n - 1)
    return [BLUE_RAMP[round(i * step)] for i in range(n)]


def render_bar(df: pd.DataFrame, y: str, top_n: int | None, height: int | None = None) -> None:
    data = (df.head(top_n) if top_n else df).copy()
    colors = _gradient_colors(len(data))
    fig = px.bar(
        data,
        x="job_count",
        y=y,
        orientation="h",
        text_auto=True,
        hover_data=["tech_group"],
        labels={"job_count": "Jobs", y: "", "tech_group": "Grupo"},
    )
    fig.update_traces(marker_color=colors, textposition="outside", textfont={"color": "#0A0A0A"})
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=height or max(400, 26 * len(data)),
        showlegend=False,
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data(ttl=600)
def load_available_roles(scope: str) -> list[str]:
    """Roles disponibles para filtrar, ordenados por frecuencia."""
    date_filter = (
        "and snapshot_date = (select max(snapshot_date) from analytics.int_job_technologies)"
        if scope == "Hoy"
        else ""
    )
    query = f"""
        SELECT technology, count(distinct job_key) as n
        FROM analytics.int_job_technologies
        WHERE kind = 'role' {date_filter}
        GROUP BY technology
        ORDER BY n DESC
    """
    with connect() as conn:
        return pd.read_sql(query, conn)["technology"].tolist()


@st.cache_data(ttl=600)
def load_tools_filtered_by_roles(selected_roles: list[str], scope: str) -> pd.DataFrame:
    """Herramientas mencionadas SOLO en ofertas que también mencionan alguno de los roles."""
    date_filter = (
        "and snapshot_date = (select max(snapshot_date) from analytics.int_job_technologies)"
        if scope == "Hoy"
        else ""
    )
    query = f"""
        with role_jobs as (
            select distinct job_key
            from analytics.int_job_technologies
            where kind = 'role' and technology = ANY(%(roles)s) {date_filter}
        )
        select t.technology, t.tech_group, t.kind, count(distinct t.job_key) as job_count
        from analytics.int_job_technologies t
        join role_jobs rj on rj.job_key = t.job_key
        where t.kind = 'tool' {date_filter}
        group by t.technology, t.tech_group, t.kind
        order by job_count desc
    """
    with connect() as conn:
        return pd.read_sql(query, conn, params={"roles": selected_roles})


def main() -> None:
    st.title("📊 MarketPulse")
    st.caption("Inteligencia del mercado laboral tech remoto · Himalayas + RemoteOK + Hacker News")

    view = st.segmented_control(
        "Vista", options=["Hoy", "Acumulado"], default="Hoy", label_visibility="collapsed"
    )
    view = view or "Hoy"

    if view == "Hoy":
        df = load_demand_today()
        scope_caption = "Snapshot del día más reciente."
    else:
        df = load_demand_cumulative()
        scope_caption = (
            "Cada oferta cuenta una sola vez en toda la historia capturada, "
            "sin duplicar por días publicada."
        )

    if df.empty:
        st.warning("No hay datos todavía. Corre el pipeline de ingesta primero.")
        return

    st.caption(scope_caption)

    df_tools = df[df["kind"] == "tool"].copy()
    df_roles = df[df["kind"] == "role"].copy()
    df_concepts = df[df["kind"] == "concept"].copy()

    total_mentions = int(df["job_count"].sum())
    tool_mentions = int(df_tools["job_count"].sum())
    other_mentions = int(df[df["kind"] == "other"]["job_count"].sum())
    tool_coverage_pct = (tool_mentions / total_mentions * 100) if total_mentions else 0

    scope_label = "histórico" if view == "Acumulado" else "hoy"

    col1, col2, col3, col4 = st.columns(4)
    with col1, st.container(border=True):
        st.metric(f"Herramientas rastreadas ({scope_label})", len(df_tools))
    with col2, st.container(border=True):
        st.metric(f"Menciones a herramientas ({scope_label})", f"{tool_mentions:,}")
    with col3, st.container(border=True):
        st.metric(f"% del total que es herramienta ({scope_label})", f"{tool_coverage_pct:.0f}%")
    with col4, st.container(border=True):
        st.metric("Fuentes activas", 3)

    tab_resumen, tab_tools, tab_roles, tab_cob = st.tabs(
        ["Resumen", "Herramientas", "Roles y temas", "Cobertura"]
    )

    with tab_resumen:
        left, right = st.columns([3, 2])
        with left:
            st.subheader("Top 10 herramientas más pedidas")
            render_bar(df_tools, y="technology", top_n=10)
        with right:
            st.subheader("Estado del pipeline")
            status = load_pipeline_status()
            for _, row in status.iterrows():
                with st.container(border=True):
                    st.markdown(
                        f"**{row['source'].title()}** · "
                        f"última carga {row['last_load']:%d %b %H:%M} UTC · "
                        f"{row['snapshots']} snapshots"
                    )

    with tab_tools:
        st.subheader("Herramientas más demandadas")
        available_roles = load_available_roles(view)
        selected_roles = st.multiselect(
            "Filtrar por rol/disciplina (opcional)",
            options=available_roles,
            help="Muestra solo herramientas en ofertas que también mencionan estos roles.",
        )
        if selected_roles:
            filtered = load_tools_filtered_by_roles(selected_roles, view)
            st.caption(f"Herramientas en ofertas de: {', '.join(selected_roles)}.")
            render_bar(filtered, y="technology", top_n=25)
        else:
            st.caption(
                "Lenguajes, frameworks, bases de datos, cloud y devops "
                "que las ofertas piden saber usar."
            )
            render_bar(df_tools, y="technology", top_n=25)

    with tab_roles:
        st.subheader("Roles y disciplinas mencionados")
        st.caption("A qué tipo de puesto corresponde la oferta — no es una herramienta a aprender.")
        render_bar(df_roles, y="technology", top_n=None, height=280)

        st.subheader("Conceptos y temas en auge")
        st.caption(
            "Términos generales que aparecen en las ofertas (IA, Big Data, DevOps...). "
            "No indican qué herramienta específica se usa — para eso, ver la pestaña Herramientas."
        )
        render_bar(df_concepts, y="technology", top_n=None, height=320)

    with tab_cob:
        st.subheader("¿De qué tipo son las menciones?")
        st.caption(
            "Cada mención cae en una de estas categorías: herramienta concreta, rol/disciplina, "
            "concepto general, o sin clasificar por el diccionario todavía."
        )
        st.progress(tool_coverage_pct / 100, text=f"{tool_coverage_pct:.0f}% son herramientas")

        breakdown = (
            df.groupby("kind", as_index=False)["job_count"]
            .sum()
            .sort_values("job_count", ascending=False)
        )
        fig = px.bar(
            breakdown,
            x="job_count",
            y="kind",
            orientation="h",
            color="kind",
            color_discrete_map={
                "tool": "#D85A30",
                "role": "#B4B2A9",
                "concept": "#EF9F27",
                "other": "#D3D1C7",
            },
            labels={"job_count": "Menciones", "kind": ""},
            text_auto=True,
        )
        fig.update_traces(textposition="outside", textfont={"color": "#3D3929"})
        fig.update_layout(
            showlegend=False,
            height=260,
            margin={**PLOTLY_LAYOUT["margin"], "r": 60},
            **{k: v for k, v in PLOTLY_LAYOUT.items() if k != "margin"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Menciones sin clasificar (other)", f"{other_mentions:,}")
        st.caption(
            "Auditoría (03/07): estas menciones son mayormente ofertas no técnicas "
            "(asistentes, ventas, coordinación) que no mencionan ningún tool/rol/concepto "
            "rastreado — no tecnologías escondidas que falten en el diccionario. "
            "Roadmap: filtrar ofertas no técnicas en la ingesta, en vez de seguir "
            "ampliando el seed."
        )


if __name__ == "__main__":
    main()
