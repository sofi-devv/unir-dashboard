from __future__ import annotations

import base64
import html
import io
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

st.set_page_config(
    page_title="UNIR · Competencias en analítica (PRELIMINAR)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Palette & Constants
# ---------------------------------------------------------------------------
PRIMARY_NAVY = "#1F4E79"
PLANES_BLUE = "#8FB3D1"
CONSULTA_TAUPE = "#A88B73"
TEXT_DARK = "#1A2332"
TEXT_MUTED = "#475569"
BORDER_SUBTLE = "#E2E8F0"
BG_SUBTLE = "#F8FAFC"

COLOR_MAP_FUENTE = {
    "Ofertas": PRIMARY_NAVY,
    "Planes de estudio (solo documentos)": PLANES_BLUE,
    "Planes de estudio (con consulta)": CONSULTA_TAUPE,
}

MEDIDA_LABELS = {
    "explicita": "Explícita (nivel 2–3)",
    "aplicada": "Aplicada (nivel 3)",
    "parcial": "Parcial (nivel 1)",
    "sin_mencion": "Sin mención (nivel 0)",
}

NIVEL_META = [
    (3, "3 · Explícita aplicada", "#1F4E79", "#FFFFFF"),
    (2, "2 · Explícita", "#5B8FA8", "#FFFFFF"),
    (1, "1 · Parcial", "#F2C166", "#1A2332"),
    (0, "0 · Sin mención (propuesto)", "#CBD5E1", "#1E293B"),
]

CATEGORY_ORDER = [
    "Habilidades técnicas",
    "Habilidades transversales",
    "Trabajo en proyectos",
    "Inglés",
]

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    color: #1A2332;
    background-color: #FFFFFF;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDeployButton"] {display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
header[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    background: transparent !important;
}

/* Main container spacing */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1380px !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }
}

/* Header */
.app-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding-bottom: 1.15rem;
    margin-bottom: 1.15rem;
    border-bottom: 1px solid #E2E8F0;
}
.app-logo-wrap {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding-right: 1.5rem;
    border-right: 1px solid #E2E8F0;
}
.app-logo-wrap img {
    height: 54px;
    width: auto;
    display: block;
}
.app-title-wrap {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
.app-eyebrow {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #1F4E79;
}
.app-title {
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.25;
    color: #1A2332;
    margin: 0;
}

/* Preliminary banner */
.prelim-banner {
    background-color: #FFF3CD;
    border: 1px solid #F6D87E;
    border-left: 5px solid #B45309;
    border-radius: 8px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 1.35rem;
    color: #4A3200;
}
.prelim-title {
    font-size: 1rem;
    font-weight: 700;
    color: #4A3200;
    margin-bottom: 0.2rem;
}
.prelim-sub {
    font-size: 0.9rem;
    line-height: 1.45;
    color: #5C4008;
}

/* KPI grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 1.6rem;
}
@media (max-width: 960px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top: 3px solid #1F4E79;
    border-radius: 10px;
    padding: 1rem 1.15rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.15;
    color: #1F4E79;
    font-variant-numeric: tabular-nums;
    margin-bottom: 0.25rem;
}
.kpi-label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1A2332;
    margin-bottom: 0.2rem;
}
.kpi-note {
    font-size: 0.84rem;
    color: #475569;
    line-height: 1.35;
}

/* Tabs */
[data-baseweb="tab-list"] {
    gap: 2rem;
    border-bottom: 2px solid #E2E8F0;
    margin-bottom: 1.25rem;
}
[data-baseweb="tab"] {
    font-size: 1.02rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    padding: 0.65rem 0.25rem !important;
    background: transparent !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #1F4E79 !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #1F4E79 !important;
    height: 3px !important;
}

/* Section headings */
.module-question {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1A2332;
    line-height: 1.4;
    margin: 0.15rem 0 0.45rem 0;
}
.def-strip {
    font-size: 0.88rem;
    color: #475569;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.6rem 0.95rem;
    margin-bottom: 1rem;
    line-height: 1.45;
}
.chart-heading {
    font-size: 1.06rem;
    font-weight: 700;
    color: #1A2332;
    margin: 1.25rem 0 0.2rem 0;
}
.chart-sub {
    font-size: 0.89rem;
    color: #475569;
    margin-bottom: 0.65rem;
    line-height: 1.45;
}

/* Callouts */
.callout-warn {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #D97706;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    color: #4A3200;
    margin: 0.75rem 0 1rem 0;
    line-height: 1.45;
}
.callout-info {
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #1F4E79;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    color: #1E293B;
    margin: 0.75rem 0 1rem 0;
    line-height: 1.45;
}

/* Survey status cards */
.survey-flags-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 0.75rem 0 1.15rem 0;
}
@media (max-width: 900px) {
    .survey-flags-grid { grid-template-columns: 1fr; }
}
.flag-card {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 0.75rem 0.95rem;
    font-size: 0.88rem;
    color: #4A3200;
    line-height: 1.4;
}
.flag-card.neutral {
    background: #F8FAFC;
    border-color: #CBD5E1;
    color: #1E293B;
}
.flag-badge {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
    background: #FDE68A;
    color: #78350F;
    margin-bottom: 0.35rem;
}
.flag-badge.neutral {
    background: #E2E8F0;
    color: #334155;
}

/* Detail HTML Table */
.detail-table-wrap {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow-x: auto;
    background: #FFFFFF;
    margin-top: 0.5rem;
}
table.detail-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    line-height: 1.45;
}
table.detail-table thead th {
    background: #F8FAFC;
    color: #1A2332;
    font-weight: 600;
    text-align: left;
    padding: 0.7rem 0.8rem;
    border-bottom: 1px solid #CBD5E1;
    white-space: nowrap;
}
table.detail-table tbody td {
    padding: 0.65rem 0.8rem;
    border-bottom: 1px solid #EEF2F6;
    vertical-align: top;
    color: #1E293B;
}
table.detail-table tbody tr:last-child td {
    border-bottom: none;
}
table.detail-table tbody tr:hover {
    background: #F8FAFC;
}
.lvl-pill {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
}
.lvl-3 { background: #1F4E79; color: #FFFFFF; }
.lvl-2 { background: #5B8FA8; color: #FFFFFF; }
.lvl-1 { background: #FEF3C7; color: #78350F; border: 1px solid #FDE68A; }
.lvl-0 { background: #F1F5F9; color: #475569; }

/* Multiselect tags */
[data-baseweb="tag"] {
    max-width: 100% !important;
}
[data-baseweb="tag"] span {
    max-width: 100% !important;
}

/* Filter container polish */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #F8FAFC;
    border-color: #E2E8F0 !important;
    border-radius: 10px !important;
}

/* Footer */
.footer-box {
    margin-top: 2.5rem;
    padding: 1.15rem 1.35rem;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    font-size: 0.88rem;
    color: #475569;
    line-height: 1.55;
}
.footer-box strong {
    color: #1A2332;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Data & Asset Loaders
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    comp = pd.read_csv(DATA_DIR / "tab_comparacion.csv")
    det = pd.read_csv(DATA_DIR / "tab_detalle.csv")
    enc = pd.read_csv(DATA_DIR / "tab_encuesta.csv")
    notas = pd.read_csv(DATA_DIR / "tab_notas.csv")
    return comp, det, enc, notas


@st.cache_data
def load_logo_b64() -> str:
    img = Image.open(ASSETS_DIR / "unir_logo.png").convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        pad = 6
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(img.width, bbox[2] + pad)
        y1 = min(img.height, bbox[3] + pad)
        img = img.crop((x0, y0, x1, y1))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


comp_df, det_df, enc_df, notas_df = load_data()
logo_b64 = load_logo_b64()

# ---------------------------------------------------------------------------
# Header, Preliminary Banner & 4 KPI Cards
# ---------------------------------------------------------------------------
st.markdown(
    f"""
<div class="app-header">
    <div class="app-logo-wrap">
        <img src="data:image/png;base64,{logo_b64}" alt="Logotipo UNIR" />
    </div>
    <div class="app-title-wrap">
        <div class="app-eyebrow">Proyecto Analítica · Relectura preliminar 30-oct-2026</div>
        <h1 class="app-title">Competencias en analítica: mercado vs. planes de estudio UNIR</h1>
    </div>
</div>

<div class="prelim-banner">
    <div class="prelim-title">PRELIMINAR · Cifras sujetas a validación oficial</div>
    <div class="prelim-sub">
        Relectura del 30-oct-2026 sobre 51 avisos completos y 29 planes (consulta aparte).
        Pendiente del clasificador y el juez oficiales. N de ofertas = 51, no 75.
        No usar las columnas antiguas de la v9 con N=75.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

n_ofertas = int(comp_df.loc[comp_df["fuente"] == "Ofertas", "N"].max())
n_planes = int(
    comp_df.loc[comp_df["fuente"] == "Planes de estudio (solo documentos)", "N"].max()
)
n_encuesta = int(enc_df["N_formulario"].max())
n_vars = int(comp_df["codigo"].nunique())

st.markdown(
    f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-value">{n_ofertas}</div>
        <div class="kpi-label">Ofertas analizadas</div>
        <div class="kpi-note">Avisos completos (de 75 originales; 24 ya no disponibles)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{n_planes}</div>
        <div class="kpi-label">Planes de estudio</div>
        <div class="kpi-note">Documentos curriculares (consulta WhatsApp aparte)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{n_encuesta}</div>
        <div class="kpi-label">Respuestas de encuesta</div>
        <div class="kpi-note">Procesada el 14-oct-2026 (sin cambios el 30-oct)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{n_vars}</div>
        <div class="kpi-label">Variables</div>
        <div class="kpi-note">4 categorías · Todas en estado preliminar</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Two Modules (Tabs)
# ---------------------------------------------------------------------------
tab_comp, tab_vis = st.tabs(["Comparación", "Visualización"])

# ===========================================================================
# TAB 1: COMPARACIÓN
# ===========================================================================
with tab_comp:
    st.markdown(
        '<div class="module-question">¿En qué variables el mercado (ofertas) pide de forma explícita algo distinto de lo que enseñan los planes de estudio?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="def-strip">'
        "<strong>Definiciones:</strong> Explícita = nivel 2 o 3 · Aplicada = nivel 3 · "
        "Parcial = nivel 1 · Sin mención = nivel 0 (propuesto, pendiente de confirmación humana). "
        "Comparador por defecto para planes: <strong>solo documentos</strong>."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.0, 1.25, 1.05, 2.2])
        with c1:
            cat_options = ["Todas las categorías"] + [
                c for c in CATEGORY_ORDER if c in comp_df["categoria"].unique()
            ]
            sel_cat_comp = st.selectbox(
                "Categoría",
                options=cat_options,
                index=0,
                key="comp_cat",
            )
        with c2:
            if sel_cat_comp == "Todas las categorías":
                avail_vars = sorted(comp_df["variable"].unique().tolist())
            else:
                avail_vars = sorted(
                    comp_df.loc[comp_df["categoria"] == sel_cat_comp, "variable"]
                    .unique()
                    .tolist()
                )
            sel_vars_comp = st.multiselect(
                "Variable",
                options=avail_vars,
                default=[],
                placeholder="Todas las variables",
                key="comp_var",
            )
        with c3:
            medida_keys = ["explicita", "aplicada", "parcial", "sin_mencion"]
            sel_medida = st.selectbox(
                "Medida",
                options=medida_keys,
                index=0,
                format_func=lambda k: MEDIDA_LABELS[k],
                key="comp_medida",
            )
        with c4:
            fuente_options = [
                "Ofertas",
                "Planes de estudio (solo documentos)",
                "Planes de estudio (con consulta)",
            ]
            sel_fuentes = st.multiselect(
                "Fuente",
                options=fuente_options,
                default=["Ofertas", "Planes de estudio (solo documentos)"],
                placeholder="Selecciona al menos una fuente",
                key="comp_fuente",
            )

    if not sel_fuentes:
        st.warning("Selecciona al menos una fuente en los filtros superiores para ver los resultados.")
    else:
        if (
            "Planes de estudio (con consulta)" in sel_fuentes
            and sel_medida != "explicita"
        ):
            st.markdown(
                '<div class="callout-info">'
                "<strong>Nota sobre «Planes de estudio (con consulta)»:</strong> la hoja v9 solo publica "
                "la medida <strong>explícita (nivel 2–3)</strong> para esta variante. No se inventaron "
                "cifras de aplicada, parcial ni sin mención."
                "</div>",
                unsafe_allow_html=True,
            )

        filt_comp = comp_df[
            (comp_df["medida"] == sel_medida)
            & (comp_df["fuente"].isin(sel_fuentes))
            & (comp_df["estado"] == "preliminar")
        ].copy()

        if sel_cat_comp != "Todas las categorías":
            filt_comp = filt_comp[filt_comp["categoria"] == sel_cat_comp]
        if sel_vars_comp:
            filt_comp = filt_comp[filt_comp["variable"].isin(sel_vars_comp)]

        if filt_comp.empty:
            st.info(
                "No hay filas disponibles para la combinación de filtros seleccionada."
            )
        else:
            if "Toma de decisiones" in filt_comp["variable"].values:
                st.markdown(
                    '<div class="callout-warn">'
                    "<strong>Nota metodológica sobre «Toma de decisiones»:</strong> variable inestable "
                    "en la ronda previa (el juez coincidió en 9 de 24) y pendiente de re-juzgamiento "
                    "oficial. No se debe afirmar como conclusión."
                    "</div>",
                    unsafe_allow_html=True,
                )

            # Determine variable sort order (descending by Ofertas, else first active fuente)
            active_sources = [f for f in sel_fuentes if f in filt_comp["fuente"].unique()]
            sort_source = "Ofertas" if "Ofertas" in active_sources else active_sources[0]
            sort_ref = (
                filt_comp[filt_comp["fuente"] == sort_source]
                .sort_values(["porcentaje", "variable"], ascending=[False, True])["variable"]
                .tolist()
            )
            # Include any variable missing from sort_source at the end
            for v in filt_comp["variable"].unique():
                if v not in sort_ref:
                    sort_ref.append(v)

            # For horizontal bars with top-most highest, pass reversed order on y
            y_order_asc = list(reversed(sort_ref))
            n_shown_vars = len(sort_ref)

            st.markdown(
                f'<div class="chart-heading">Comparación pareada por variable · {MEDIDA_LABELS[sel_medida]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="chart-sub">Mostrando {n_shown_vars} variables · Etiquetas en formato porcentaje redondeado y recuento exacto (n de N).</div>',
                unsafe_allow_html=True,
            )

            fig_comp = go.Figure()
            # Add traces in reverse display order so first source appears at top of each group
            for fuente_name in reversed(active_sources):
                sub = (
                    filt_comp[filt_comp["fuente"] == fuente_name]
                    .set_index("variable")
                    .reindex(y_order_asc)
                    .reset_index()
                )
                sub = sub.dropna(subset=["porcentaje"])
                labels_text = [
                    f"{round(p * 100):.0f}% ({ndn})"
                    for p, ndn in zip(sub["porcentaje"], sub["n_de_N"])
                ]
                hover_text = [
                    f"<b>{v}</b><br>{fuente_name}<br>"
                    f"Porcentaje: {p * 100:.1f}% ({ndn})<br>"
                    f"Categoría: {cat}<br>Estado: preliminar"
                    for v, p, ndn, cat in zip(
                        sub["variable"], sub["porcentaje"], sub["n_de_N"], sub["categoria"]
                    )
                ]
                fig_comp.add_trace(
                    go.Bar(
                        y=sub["variable"],
                        x=sub["porcentaje"],
                        name=fuente_name,
                        orientation="h",
                        marker=dict(
                            color=COLOR_MAP_FUENTE.get(fuente_name, "#64748B"),
                            line=dict(width=0),
                        ),
                        text=labels_text,
                        textposition="outside",
                        cliponaxis=False,
                        textfont=dict(size=13.5, color=TEXT_DARK),
                        hovertext=hover_text,
                        hoverinfo="text",
                    )
                )

            row_step = 40 if len(active_sources) <= 2 else 52
            chart_height = max(380, n_shown_vars * row_step + 110)

            fig_comp.update_layout(
                barmode="group",
                bargap=0.22,
                bargroupgap=0.08,
                height=chart_height,
                margin=dict(l=10, r=140, t=64, b=36),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(
                    family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                    size=14,
                    color=TEXT_DARK,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                    traceorder="reversed",
                    font=dict(size=14, color=TEXT_DARK),
                ),
                xaxis=dict(
                    range=[0, 1.18],
                    tickformat=".0%",
                    dtick=0.2,
                    gridcolor="#EEF2F6",
                    zerolinecolor="#CBD5E1",
                    tickfont=dict(size=14, color=TEXT_MUTED),
                    title=dict(text="Porcentaje sobre total de la fuente", font=dict(size=14, color=TEXT_MUTED)),
                ),
                yaxis=dict(
                    categoryorder="array",
                    categoryarray=y_order_asc,
                    tickfont=dict(size=14, color=TEXT_DARK),
                    automargin=True,
                ),
            )

            st.plotly_chart(
                fig_comp,
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False},
            )

            # Supporting Table
            st.markdown(
                '<div class="chart-heading">Tabla de apoyo (valores exactos)</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="chart-sub">Lectura exacta de n de N y porcentaje con un decimal, sin aproximar.</div>',
                unsafe_allow_html=True,
            )

            rank_map = {v: i for i, v in enumerate(sort_ref)}
            fuente_rank = {f: i for i, f in enumerate(fuente_options)}
            tbl_comp = filt_comp.copy()
            tbl_comp["_vrank"] = tbl_comp["variable"].map(rank_map)
            tbl_comp["_frank"] = tbl_comp["fuente"].map(fuente_rank)
            tbl_comp = tbl_comp.sort_values(["_vrank", "_frank"]).drop(
                columns=["_vrank", "_frank"]
            )
            tbl_comp["Porcentaje (%)"] = (tbl_comp["porcentaje"] * 100).round(1)
            tbl_display = tbl_comp[
                ["variable", "categoria", "fuente", "n_de_N", "Porcentaje (%)", "estado"]
            ].rename(
                columns={
                    "variable": "Variable",
                    "categoria": "Categoría",
                    "fuente": "Fuente",
                    "n_de_N": "n de N",
                    "estado": "Estado",
                }
            )

            st.dataframe(
                tbl_display,
                use_container_width=True,
                hide_index=True,
                height=min(460, 42 + len(tbl_display) * 35),
                column_config={
                    "Variable": st.column_config.TextColumn("Variable", width="medium"),
                    "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
                    "Fuente": st.column_config.TextColumn("Fuente", width="medium"),
                    "n de N": st.column_config.TextColumn("n de N", width="small"),
                    "Porcentaje (%)": st.column_config.NumberColumn(
                        "Porcentaje", format="%.1f%%", width="small"
                    ),
                    "Estado": st.column_config.TextColumn("Estado", width="small"),
                },
            )

            # Optional Brecha view (Ofertas vs Planes solo documentos)
            if (
                "Ofertas" in active_sources
                and "Planes de estudio (solo documentos)" in active_sources
            ):
                piv = filt_comp[
                    filt_comp["fuente"].isin(
                        ["Ofertas", "Planes de estudio (solo documentos)"]
                    )
                ].pivot(index="variable", columns="fuente", values="porcentaje")
                if (
                    "Ofertas" in piv.columns
                    and "Planes de estudio (solo documentos)" in piv.columns
                ):
                    piv = piv.dropna().copy()
                    piv["brecha_pp"] = (
                        piv["Ofertas"] - piv["Planes de estudio (solo documentos)"]
                    ) * 100.0
                    piv = piv.sort_values("brecha_pp", ascending=True).reset_index()

                    st.markdown(
                        f'<div class="chart-heading">Brecha simple en puntos porcentuales (Ofertas − Planes solo documentos) · {MEDIDA_LABELS[sel_medida]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        '<div class="chart-sub">'
                        "Diferencia calculada directamente entre los porcentajes de la tabla superior "
                        "(% Ofertas − % Planes solo documentos). Valores positivos (+ pp) indican mayor "
                        "presencia en ofertas; negativos (− pp), mayor presencia en planes. "
                        "No se recalculan uniones agrupadas."
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    bar_colors = [
                        PRIMARY_NAVY if val >= 0 else PLANES_BLUE
                        for val in piv["brecha_pp"]
                    ]
                    bar_labels = [
                        f"{val:+.1f} pp" for val in piv["brecha_pp"]
                    ]
                    hover_brecha = [
                        f"<b>{v}</b><br>Ofertas: {o*100:.1f}%<br>"
                        f"Planes (solo documentos): {pl*100:.1f}%<br>"
                        f"Brecha: {b:+.1f} pp"
                        for v, o, pl, b in zip(
                            piv["variable"],
                            piv["Ofertas"],
                            piv["Planes de estudio (solo documentos)"],
                            piv["brecha_pp"],
                        )
                    ]

                    fig_brecha = go.Figure(
                        go.Bar(
                            y=piv["variable"],
                            x=piv["brecha_pp"],
                            orientation="h",
                            marker=dict(color=bar_colors),
                            text=bar_labels,
                            textposition="outside",
                            cliponaxis=False,
                            textfont=dict(size=13.5, color=TEXT_DARK),
                            hovertext=hover_brecha,
                            hoverinfo="text",
                        )
                    )
                    min_b = min(-15.0, float(piv["brecha_pp"].min()) - 14.0)
                    max_b = max(15.0, float(piv["brecha_pp"].max()) + 16.0)
                    fig_brecha.update_layout(
                        height=max(380, len(piv) * 28 + 100),
                        margin=dict(l=10, r=70, t=24, b=40),
                        plot_bgcolor="#FFFFFF",
                        paper_bgcolor="#FFFFFF",
                        font=dict(
                            family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                            size=14,
                            color=TEXT_DARK,
                        ),
                        showlegend=False,
                        xaxis=dict(
                            range=[min_b, max_b],
                            ticksuffix=" pp",
                            gridcolor="#EEF2F6",
                            zeroline=True,
                            zerolinecolor="#64748B",
                            zerolinewidth=1.5,
                            tickfont=dict(size=14, color=TEXT_MUTED),
                            title=dict(
                                text="Diferencia en puntos porcentuales (Ofertas − Planes)",
                                font=dict(size=14, color=TEXT_MUTED),
                            ),
                        ),
                        yaxis=dict(
                            tickfont=dict(size=14, color=TEXT_DARK),
                            automargin=True,
                        ),
                    )
                    st.plotly_chart(
                        fig_brecha,
                        use_container_width=True,
                        theme=None,
                config={"displayModeBar": False},
                    )


# ===========================================================================
# TAB 2: VISUALIZACIÓN (DETALLE, NIVELES 0–3 Y ENCUESTA)
# ===========================================================================
with tab_vis:
    st.markdown(
        '<div class="module-question">En una oferta o un programa concreto, ¿qué variables aparecen, con qué nivel y con qué cita?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="def-strip">'
        "<strong>Niveles de evidencia:</strong> 0 = sin mención (propuesto) · "
        "1 = mención parcial · 2 = mención explícita · 3 = explícita con aplicación. "
        "<strong>Explícita</strong> agrupa los niveles 2 y 3."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        v1, v2, v3, v4 = st.columns([1.05, 1.55, 1.25, 1.55])
        with v1:
            sel_fuente_det = st.selectbox(
                "Fuente",
                options=["Todas", "Ofertas", "Planes de estudio"],
                index=0,
                key="vis_fuente",
            )
        with v2:
            if sel_fuente_det == "Todas":
                avail_ids = sorted(det_df["id"].unique().tolist())
            else:
                avail_ids = sorted(
                    det_df.loc[det_df["fuente"] == sel_fuente_det, "id"]
                    .unique()
                    .tolist()
                )
            sel_ids_det = st.multiselect(
                "Oferta o programa",
                options=avail_ids,
                default=[],
                placeholder=f"Todos ({len(avail_ids)} unidades)",
                key="vis_id",
            )
        with v3:
            cat_opts_det = ["Todas las categorías"] + [
                c for c in CATEGORY_ORDER if c in det_df["categoria"].unique()
            ]
            sel_cat_det = st.selectbox(
                "Categoría",
                options=cat_opts_det,
                index=0,
                key="vis_cat",
            )
        with v4:
            if sel_cat_det == "Todas las categorías":
                avail_vars_det = sorted(det_df["variable"].unique().tolist())
            else:
                avail_vars_det = sorted(
                    det_df.loc[det_df["categoria"] == sel_cat_det, "variable"]
                    .unique()
                    .tolist()
                )
            sel_vars_det = st.multiselect(
                "Variable",
                options=avail_vars_det,
                default=[],
                placeholder="Todas las variables",
                key="vis_var",
            )

    filt_det = det_df.copy()
    if sel_fuente_det != "Todas":
        filt_det = filt_det[filt_det["fuente"] == sel_fuente_det]
    if sel_ids_det:
        filt_det = filt_det[filt_det["id"].isin(sel_ids_det)]
    if sel_cat_det != "Todas las categorías":
        filt_det = filt_det[filt_det["categoria"] == sel_cat_det]
    if sel_vars_det:
        filt_det = filt_det[filt_det["variable"].isin(sel_vars_det)]

    if filt_det.empty:
        st.info("No hay registros de detalle para la selección actual.")
    else:
        n_units = filt_det["id"].nunique()
        n_vars_det = filt_det["variable"].nunique()

        st.markdown(
            '<div class="chart-heading">Distribución de niveles (0–3) por variable (100 % apilado)</div>',
            unsafe_allow_html=True,
        )
        legend_items_html = "".join(
            f'<span style="display:inline-flex;align-items:center;gap:0.4rem;margin-right:1.2rem;font-size:0.88rem;color:#1A2332;">'
            f'<span style="width:13px;height:13px;border-radius:3px;background:{bg_col};display:inline-block;border:1px solid rgba(15,23,42,0.12);"></span>'
            f'{lbl}</span>'
            for _, lbl, bg_col, _ in NIVEL_META
        )
        st.markdown(
            f'<div class="chart-sub" style="margin-bottom:0.45rem;">'
            f"Sobre <strong>{n_units}</strong> unidad(es) seleccionada(s) y <strong>{n_vars_det}</strong> variable(s) · "
            f"Ordenado por porcentaje explícito (nivel 2–3)."
            f"</div>"
            f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:0.25rem;margin:0.2rem 0 0.55rem 0;">'
            f"{legend_items_html}"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Compute 100% stacked counts per variable x nivel
        counts = (
            filt_det.groupby(["variable", "nivel"])
            .size()
            .unstack(fill_value=0)
        )
        for lvl, _, _, _ in NIVEL_META:
            if lvl not in counts.columns:
                counts[lvl] = 0
        counts = counts[[0, 1, 2, 3]]
        totals = counts.sum(axis=1)
        pcts = counts.div(totals, axis=0)

        # Sort by explicit share (lvl 2 + lvl 3) desc, then partial (lvl 1) desc
        sort_df = pd.DataFrame(
            {
                "explicit_pct": pcts[2] + pcts[3],
                "partial_pct": pcts[1],
            },
            index=pcts.index,
        ).sort_values(["explicit_pct", "partial_pct"], ascending=[False, False])
        ordered_vars = list(reversed(sort_df.index.tolist()))

        fig_stack = go.Figure()
        # Add in order 3 -> 2 -> 1 -> 0 so Explicit (3, 2) sits cleanly on the left
        for lvl, lbl, bg_col, txt_col in NIVEL_META:
            vals = [float(pcts.loc[v, lvl]) for v in ordered_vars]
            raw_n = [int(counts.loc[v, lvl]) for v in ordered_vars]
            tot_n = [int(totals.loc[v]) for v in ordered_vars]
            seg_text = [f"{p * 100:.0f}%" if p >= 0.08 else "" for p in vals]
            hover_seg = [
                f"<b>{v}</b><br>{lbl}<br>{p * 100:.1f}% ({rn} de {tn})"
                for v, p, rn, tn in zip(ordered_vars, vals, raw_n, tot_n)
            ]
            fig_stack.add_trace(
                go.Bar(
                    y=ordered_vars,
                    x=vals,
                    name=lbl,
                    orientation="h",
                    marker=dict(color=bg_col, line=dict(color="#FFFFFF", width=0.8)),
                    text=seg_text,
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(size=13, color=txt_col),
                    hovertext=hover_seg,
                    hoverinfo="text",
                )
            )

        fig_stack.update_layout(
            barmode="stack",
            bargap=0.22,
            height=max(400, n_vars_det * 35 + 80),
            margin=dict(l=10, r=24, t=12, b=36),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            showlegend=False,
            font=dict(
                family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                size=14,
                color=TEXT_DARK,
            ),
            xaxis=dict(
                range=[0, 1.0],
                tickformat=".0%",
                dtick=0.2,
                gridcolor="#EEF2F6",
                tickfont=dict(size=14, color=TEXT_MUTED),
                title=dict(text="Proporción de unidades por nivel (0–3)", font=dict(size=14, color=TEXT_MUTED)),
            ),
            yaxis=dict(
                categoryorder="array",
                categoryarray=ordered_vars,
                tickfont=dict(size=14, color=TEXT_DARK),
                automargin=True,
            ),
        )
        st.plotly_chart(
            fig_stack,
            use_container_width=True,
            theme=None,
                config={"displayModeBar": False},
        )

        # Detail & Quotes Table
        st.markdown(
            '<div class="chart-heading">Tabla de detalle y citas literales verificadas</div>',
            unsafe_allow_html=True,
        )
        ctrl_l, ctrl_m, ctrl_r = st.columns([1.8, 1.5, 1.2])
        with ctrl_l:
            only_mentions = st.checkbox(
                "Mostrar solo registros con evidencia (niveles 1–3)",
                value=True,
                key="vis_only_mentions",
            )
        with ctrl_m:
            quote_search = st.text_input(
                "Buscar texto en cita o ID",
                value="",
                placeholder="Ej. Power BI, V01, PROG_...",
                label_visibility="collapsed",
                key="vis_quote_search",
            )

        tbl_det = filt_det.copy()
        if only_mentions:
            tbl_det = tbl_det[tbl_det["nivel"] >= 1]
        if quote_search.strip():
            q = quote_search.strip().lower()
            mask = (
                tbl_det["id"].astype(str).str.lower().str.contains(q, na=False)
                | tbl_det["variable"].astype(str).str.lower().str.contains(q, na=False)
                | tbl_det["cita_corta"].astype(str).str.lower().str.contains(q, na=False)
                | tbl_det["cita_consulta_corta"].astype(str).str.lower().str.contains(q, na=False)
            )
            tbl_det = tbl_det[mask]

        tbl_det = tbl_det.sort_values(
            ["nivel", "id", "variable"], ascending=[False, True, True]
        )

        has_planes = "Planes de estudio" in tbl_det["fuente"].unique()
        total_rows_det = len(tbl_det)
        page_size = 10
        total_pages = max(1, (total_rows_det + page_size - 1) // page_size)

        with ctrl_r:
            csv_bytes = tbl_det.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Descargar CSV filtrado",
                data=csv_bytes,
                file_name="unir_detalle_filtrado.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown(
            f'<div class="chart-sub">Mostrando {min(page_size, total_rows_det)} de {total_rows_det:,} registros filtrados (ordenados de nivel 3 a 0). Las citas están recortadas a ~220 caracteres desde la hoja v9.</div>',
            unsafe_allow_html=True,
        )

        if total_rows_det == 0:
            st.info("No hay citas que coincidan con el filtro actual.")
        else:
            page_num = 1
            if total_pages > 1:
                p_col1, p_col2 = st.columns([1.2, 4.0])
                with p_col1:
                    page_num = int(
                        st.number_input(
                            f"Página (1–{total_pages})",
                            min_value=1,
                            max_value=total_pages,
                            value=1,
                            step=1,
                            key="vis_page_num",
                        )
                    )
            start_idx = (page_num - 1) * page_size
            page_df = tbl_det.iloc[start_idx : start_idx + page_size]

            # Build clean HTML table with full wrapping for citas
            headers_html = (
                "<th>ID</th>"
                "<th>Fuente</th>"
                "<th>Variable</th>"
                "<th>Nivel</th>"
                "<th>Expl.</th>"
                "<th>Cita literal corta</th>"
                "<th>Ubicación</th>"
            )
            if has_planes:
                headers_html += (
                    "<th>N. cons.</th>"
                    "<th>N. c/cons.</th>"
                    "<th>Cita consulta corta</th>"
                )

            rows_html = []
            for _, r in page_df.iterrows():
                lvl = int(r["nivel"])
                exp_txt = "Sí (1)" if int(r["presencia_explicita"]) == 1 else "No (0)"
                cita = (
                    html.escape(str(r["cita_corta"]))
                    if pd.notna(r["cita_corta"]) and str(r["cita_corta"]).strip()
                    else '<span style="color:#94A3B8;">—</span>'
                )
                ubic = (
                    html.escape(str(r["ubicacion"]))
                    if pd.notna(r["ubicacion"]) and str(r["ubicacion"]).strip()
                    else '<span style="color:#94A3B8;">—</span>'
                )
                fuente_short = "Planes" if r["fuente"] == "Planes de estudio" else html.escape(str(r["fuente"]))
                row_cells = (
                    f"<td style='white-space:nowrap;'><strong>{html.escape(str(r['id']))}</strong></td>"
                    f"<td style='white-space:nowrap;'>{fuente_short}</td>"
                    f"<td style='min-width:110px;max-width:155px;'>{html.escape(str(r['variable']))}</td>"
                    f'<td style="white-space:nowrap;"><span class="lvl-pill lvl-{lvl}">Nivel {lvl}</span></td>'
                    f"<td style='white-space:nowrap;'>{exp_txt}</td>"
                    f'<td style="min-width:240px;max-width:360px;">{cita}</td>'
                    f'<td style="min-width:150px;max-width:210px;word-break:break-word;font-size:0.82rem;color:#475569;">{ubic}</td>'
                )
                if has_planes:
                    nc = (
                        f"{int(r['nivel_consulta'])}"
                        if pd.notna(r["nivel_consulta"])
                        else "—"
                    )
                    ncc = (
                        f"{int(r['nivel_con_consulta'])}"
                        if pd.notna(r["nivel_con_consulta"])
                        else "—"
                    )
                    cc = (
                        html.escape(str(r["cita_consulta_corta"]))
                        if pd.notna(r["cita_consulta_corta"])
                        and str(r["cita_consulta_corta"]).strip()
                        else '<span style="color:#94A3B8;">—</span>'
                    )
                    row_cells += (
                        f"<td style='text-align:center;white-space:nowrap;'>{nc}</td>"
                        f"<td style='text-align:center;white-space:nowrap;'>{ncc}</td>"
                        f'<td style="min-width:140px;max-width:220px;font-size:0.83rem;">{cc}</td>'
                    )
                rows_html.append(f"<tr>{row_cells}</tr>")

            st.markdown(
                f"""
                <div class="detail-table-wrap">
                    <table class="detail-table">
                        <thead><tr>{headers_html}</tr></thead>
                        <tbody>{"".join(rows_html)}</tbody>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------------------------
    # Survey Section (Encuesta)
    # -----------------------------------------------------------------------
    st.markdown("<hr style='margin: 2.2rem 0 1.5rem 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
    st.markdown(
        '<div class="module-question">Encuesta · ¿Cómo se describen las personas que respondieron, y qué herramientas dicen usar?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="chart-sub">'
        "54 respuestas del formulario procesadas el 14-oct-2026 (sin IA; sin cambios en la relectura del 30-oct). "
        "Bloque separado de los niveles 0–3 de documentos y ofertas."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="survey-flags-grid">
            <div class="flag-card">
                <span class="flag-badge">P04 · Pendiente</span><br>
                Falta definir la regla para respuestas con un número de opciones distinto de 3.
            </div>
            <div class="flag-card">
                <span class="flag-badge">P09 · Pendiente</span><br>
                Escala por verificar (valores observados 1 a 8). <strong>No usar en conclusiones.</strong>
            </div>
            <div class="flag-card neutral">
                <span class="flag-badge neutral">P10 · Texto abierto</span><br>
                45 de 54 respuestas abiertas sin codificar; no se grafica distribución.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preg_meta = (
        enc_df[["pregunta", "texto_pregunta", "medida", "n_respuestas_validas", "estado"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    def format_preg(p_code: str) -> str:
        row = preg_meta[preg_meta["pregunta"] == p_code].iloc[0]
        tag = ""
        if p_code in ("P04", "P09"):
            tag = " [PENDIENTE]"
        elif p_code == "P10":
            tag = " [Texto abierto sin codificar]"
        return f"{p_code} · {row['texto_pregunta']}{tag}"

    sel_preg = st.selectbox(
        "Pregunta de la encuesta",
        options=preg_meta["pregunta"].tolist(),
        index=0,
        format_func=format_preg,
        key="enc_preg",
    )

    sub_enc = enc_df[enc_df["pregunta"] == sel_preg].copy()
    preg_info = preg_meta[preg_meta["pregunta"] == sel_preg].iloc[0]

    if sel_preg == "P04":
        st.markdown(
            '<div class="callout-warn">'
            "<strong>P04 · PENDIENTE:</strong> falta definir la regla de conteo para respuestas "
            "con un número de opciones distinto de 3. Cifras preliminares sujetas a revisión."
            "</div>",
            unsafe_allow_html=True,
        )
    elif sel_preg == "P09":
        st.markdown(
            '<div class="callout-warn">'
            "<strong>P09 · PENDIENTE — NO USAR EN CONCLUSIONES:</strong> escala por verificar "
            "(valores observados 1 a 8). No presentar como resultado de alineación hasta validar "
            "el rango original del formulario."
            "</div>",
            unsafe_allow_html=True,
        )

    if sel_preg == "P10":
        st.markdown(
            '<div class="callout-info">'
            "<strong>P10 · Asignatura obligatoria que agregaría (respuesta abierta):</strong> "
            "se registraron <strong>45 de 54</strong> respuestas en texto libre sin codificar. "
            "De acuerdo con la especificación metodológica, no se grafica una distribución por opción."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # Preserve numeric scale order for P05, P07, P09; sort by porcentaje desc for categorical questions
        if sel_preg in ("P05", "P07", "P09"):
            sub_enc["_ord"] = pd.to_numeric(sub_enc["opcion"], errors="coerce")
            sub_enc = sub_enc.sort_values("_ord", ascending=False).drop(columns=["_ord"])
        else:
            sub_enc = sub_enc.sort_values(["porcentaje", "opcion"], ascending=[True, False])

        col_chart, col_tbl = st.columns([1.45, 1.05], gap="large")
        with col_chart:
            bar_col = "#B45309" if sel_preg in ("P04", "P09") else PRIMARY_NAVY
            labels_enc = [
                f"{round(p * 100):.0f}% ({int(n)} de {int(N)})"
                for p, n, N in zip(sub_enc["porcentaje"], sub_enc["n"], sub_enc["N"])
            ]
            fig_enc = go.Figure(
                go.Bar(
                    y=sub_enc["opcion"].astype(str),
                    x=sub_enc["porcentaje"],
                    orientation="h",
                    marker=dict(color=bar_col),
                    text=labels_enc,
                    textposition="outside",
                    cliponaxis=False,
                    textfont=dict(size=13.5, color=TEXT_DARK),
                    hovertemplate="<b>%{y}</b><br>%{x:.1%}<extra></extra>",
                )
            )
            fig_enc.update_layout(
                height=max(300, len(sub_enc) * 34 + 80),
                margin=dict(l=10, r=125, t=16, b=36),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(
                    family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                    size=14,
                    color=TEXT_DARK,
                ),
                xaxis=dict(
                    range=[0, max(0.35, float(sub_enc["porcentaje"].max()) * 1.32)],
                    tickformat=".0%",
                    gridcolor="#EEF2F6",
                    tickfont=dict(size=13.5, color=TEXT_MUTED),
                ),
                yaxis=dict(
                    tickfont=dict(size=13.5, color=TEXT_DARK),
                    automargin=True,
                ),
            )
            st.plotly_chart(
                fig_enc,
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False},
            )

        with col_tbl:
            tbl_enc_show = sub_enc.iloc[::-1][
                ["opcion", "n", "N", "porcentaje", "criterios_asociados"]
            ].copy()
            tbl_enc_show["Porcentaje"] = (tbl_enc_show["porcentaje"] * 100).round(1)
            tbl_enc_show["Criterios"] = tbl_enc_show["criterios_asociados"].fillna("—")
            tbl_enc_show = tbl_enc_show[
                ["opcion", "n", "N", "Porcentaje", "Criterios"]
            ].rename(columns={"opcion": "Opción"})
            st.dataframe(
                tbl_enc_show,
                use_container_width=True,
                hide_index=True,
                height=min(420, 44 + len(tbl_enc_show) * 36),
                column_config={
                    "Opción": st.column_config.TextColumn("Opción", width="medium"),
                    "n": st.column_config.NumberColumn("n", format="%d", width="small"),
                    "N": st.column_config.NumberColumn("N", format="%d", width="small"),
                    "Porcentaje": st.column_config.NumberColumn(
                        "%", format="%.1f%%", width="small"
                    ),
                    "Criterios": st.column_config.TextColumn("Criterios", width="small"),
                },
            )

# ---------------------------------------------------------------------------
# Footer & Methodological Notes
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="footer-box">
    <strong>Fuentes y estado preliminar:</strong> Cifras provenientes de la hoja
    <em>UNIR_resultados_legible_v9</em> (relectura completa del 30-oct-2026 sobre 51 avisos completos
    de 75 originales y 29 planes de estudio; encuesta procesada el 14-oct-2026 sobre 54 respuestas).
    Todas las cifras de ofertas y planes tienen estado <strong>preliminar</strong> y están pendientes de
    validación oficial con el clasificador y el juez. No se usan columnas antiguas con N=75, no se recalculan
    uniones agrupadas y no se afirman conclusiones sobre «Toma de decisiones» ni «P09».
    <strong>Uso privado para revisión de Sophie; no compartir ni publicar sin autorización.</strong>
</div>
""",
    unsafe_allow_html=True,
)

with st.expander("Ver notas metodológicas completas (30 registros de tab_notas.csv)"):
    notas_show = notas_df.rename(columns={"campo": "Campo", "contenido": "Contenido"})
    st.dataframe(
        notas_show,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "Campo": st.column_config.TextColumn("Campo", width="medium"),
            "Contenido": st.column_config.TextColumn("Contenido", width="large"),
        },
    )
