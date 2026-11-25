"""UNIR · Competencias en analítica (PRELIMINAR) — diseño compacto, una pantalla por pestaña."""
from __future__ import annotations

import base64
import io
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

BASE = Path(__file__).parent
DATA = BASE / "data"
ASSETS = BASE / "assets"

st.set_page_config(
    page_title="UNIR · Competencias en analítica (PRELIMINAR)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------- paleta
PURPLE = "#5B4FD9"   # Ofertas
BLUE = "#3B9FE0"     # Planes (solo documentos)
GREEN = "#2FB58A"    # Planes (con consulta) / positivo
GREY = "#D6DAE3"
INK = "#1F2937"
MUTED = "#6B7280"
FONT = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"

F_OF = "Ofertas"
F_PL = "Planes de estudio (solo documentos)"
F_PC = "Planes de estudio (con consulta)"
FUENTE_COLOR = {F_OF: PURPLE, F_PL: BLUE, F_PC: GREEN}
FUENTE_CORTA = {F_OF: "Ofertas", F_PL: "Planes (documentos)", F_PC: "Planes (con consulta)"}

MEDIDAS = {
    "explicita": "Explícita (nivel 2–3)",
    "aplicada": "Aplicada (nivel 3)",
    "parcial": "Parcial (nivel 1)",
    "sin_mencion": "Sin mención (nivel 0)",
}
NIVELES = [  # nivel, etiqueta, color
    (3, "3 · Explícita aplicada", PURPLE),
    (2, "2 · Explícita", "#8F86F0"),
    (1, "1 · Parcial", BLUE),
    (0, "0 · Sin mención", GREY),
]
CATEGORIAS = ["Habilidades técnicas", "Habilidades transversales", "Trabajo en proyectos", "Inglés"]

CORTO = {
    "Gestión y coordinación de proyectos": "Gestión de proyectos",
    "Necesidades o requerimientos": "Requerimientos",
    "Interacción con clientes o interesados": "Clientes e interesados",
    "Explicar a públicos no técnicos": "Explicar a no técnicos",
    "Requisito de inglés (ingreso o grado)": "Requisito de inglés",
    "Resultado de aprendizaje (inglés)": "Resultado (inglés)",
    "Uso oral o escrito del inglés": "Inglés oral/escrito",
    "Extracción y transformación": "Extracción (ETL)",
    "Visualización de datos": "Visualización",
    "Aprendizaje automático": "Aprend. automático",
    "Colaboración entre áreas": "Colaboración áreas",
    "Presentación de resultados": "Presentar resultados",
    "Lectura técnica en inglés": "Lectura en inglés",
}


def corto(v: str) -> str:
    return CORTO.get(v, v)


# ---------------------------------------------------------------- CSS
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }
.stApp { background: #F4F5F8; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stDeployButton"], .stDeployButton,
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 0.9rem 2rem 0.6rem 2rem !important; max-width: 1440px !important; }
[data-testid="stVerticalBlock"] { gap: 0.6rem; }
[data-testid="stHorizontalBlock"] { gap: 0.9rem; }

/* tarjetas */
[class*="st-key-card"] {
  background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px;
  padding: 0.75rem 0.95rem 1.0rem 0.95rem !important;
  box-shadow: 0 1px 2px rgba(17,24,39,0.04);
}
[class*="st-key-card"] [data-testid="stVerticalBlock"] { gap: 0.35rem; }
.card-title { font-size: 0.86rem; font-weight: 600; color: #374151; margin: 0; }
.card-sub { font-size: 0.78rem !important; color: #6B7280; margin: 0 0 0.1rem 0; }

/* cabecera */
.hdr { display:flex; align-items:center; gap:0.9rem; }
.hdr img { height: 30px; }
.hdr .sep { width:1px; height:28px; background:#D1D5DB; }
.hdr h1 { font-size: 1.28rem; font-weight: 700; color:#111827; margin:0; padding:0; line-height:1.2; }
.pill { display:inline-block; background:#FFF3CD; color:#7A4B00; border:1px solid #F5D77A;
  font-size:0.74rem; font-weight:700; letter-spacing:0.03em; padding:0.18rem 0.6rem; border-radius:999px; white-space:nowrap; }
.pill-sub { font-size:0.76rem; color:#6B7280; white-space:nowrap; }

/* tabs */
[data-baseweb="tab-list"] { gap: 1.6rem; border-bottom: 1px solid #E5E7EB; }
[data-baseweb="tab"] { font-size: 0.95rem !important; font-weight: 600 !important; padding: 0.35rem 0.1rem !important; background: transparent !important; }
[data-baseweb="tab"][aria-selected="true"] { color: #5B4FD9 !important; }
[data-baseweb="tab-highlight"] { background-color: #5B4FD9 !important; }
[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 0.55rem !important; }

/* sección */
.sec-h { font-size: 1.05rem; font-weight: 700; color:#111827; margin: 0; }
.sec-i { font-size: 0.88rem; color:#4B5563; margin: 0.1rem 0 0.35rem 0; }

/* KPI */
.kpi { background:#FFF; border:1px solid #E5E7EB; border-radius:12px; padding:0.6rem 0.95rem; }
.kpi .l { font-size:0.8rem; color:#6B7280; font-weight:500; }
.kpi .v { font-size:1.6rem; font-weight:700; color:#111827; line-height:1.15; }
.kpi .n { font-size:0.74rem; color:#9CA3AF; }

/* número grande */
.big { font-size: 2.6rem; font-weight: 700; color: #5B4FD9; line-height: 1.05; }
.big-l { font-size: 1.0rem; font-weight: 600; color:#111827; }
.row2 { display:flex; justify-content:space-between; font-size:0.84rem; color:#374151; margin-top:0.2rem; }
.dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:0.35rem; }
.bar { height:9px; background:#EEF0F4; border-radius:999px; overflow:hidden; margin:0.2rem 0 0.45rem 0; }
.bar > div { height:100%; border-radius:999px; }
.flag { font-size:0.82rem; color:#374151; padding:0.35rem 0; border-top:1px solid #F1F2F5; }
.flag:first-of-type { border-top:none; }
.tag { display:inline-block; font-size:0.68rem; font-weight:700; padding:0.08rem 0.42rem; border-radius:5px; margin-right:0.35rem; }
.tag.p { background:#FFF3CD; color:#7A4B00; }
.tag.o { background:#EEF0F4; color:#374151; }
.legend span { display:inline-flex; align-items:center; gap:0.3rem; margin-right:0.8rem; font-size:0.78rem; color:#374151; }
.legend i { width:10px; height:10px; border-radius:3px; display:inline-block; }
.foot { font-size:0.74rem; color:#9CA3AF; margin-top:0.1rem; }

/* widgets compactos */
[data-testid="stSelectbox"] label p, [data-testid="stMultiSelect"] label p { font-size: 0.78rem !important; color:#6B7280 !important; }
[data-baseweb="select"] > div { min-height: 34px !important; font-size: 0.88rem; }
[data-testid="stExpander"] summary p { font-size: 0.85rem; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- datos
@st.cache_data
def load():
    return (
        pd.read_csv(DATA / "tab_comparacion.csv"),
        pd.read_csv(DATA / "tab_detalle.csv"),
        pd.read_csv(DATA / "tab_encuesta.csv"),
        pd.read_csv(DATA / "tab_notas.csv"),
    )


@st.cache_data
def logo_b64() -> str:
    img = Image.open(ASSETS / "unir_logo.png").convert("RGBA")
    bb = img.getbbox()
    if bb:
        img = img.crop(bb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


comp, det, enc, notas = load()
N_OF = int(comp.loc[comp.fuente == F_OF, "N"].max())
N_PL = int(comp.loc[comp.fuente == F_PL, "N"].max())
N_ENC = int(enc["N_formulario"].max())
N_VAR = int(comp["codigo"].nunique())
N_CITAS = len(det)


def pivot(medida: str, categoria: str | None = None) -> pd.DataFrame:
    d = comp[(comp.medida == medida) & (comp.estado == "preliminar")]
    if categoria:
        d = d[d.categoria == categoria]
    p = d.pivot_table(index=["variable", "categoria"], columns="fuente", values="porcentaje").reset_index()
    nn = d.pivot_table(index="variable", columns="fuente", values="n_de_N", aggfunc="first")
    p = p.merge(nn.add_prefix("ndn_"), left_on="variable", right_index=True, how="left")
    if F_OF in p and F_PL in p:
        p["brecha"] = (p[F_OF] - p[F_PL]) * 100
    return p


def base_layout(fig: go.Figure, height: int, **kw) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=kw.pop("margin", dict(l=4, r=12, t=6, b=4)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=14, color=INK),
        hoverlabel=dict(font=dict(family=FONT, size=13)),
        **kw,
    )
    return fig


def show(fig):
    st.plotly_chart(fig, use_container_width=True, theme=None, config={"displayModeBar": False})


def card_head(title: str, sub: str = ""):
    st.markdown(
        f'<p class="card-title">{title}</p>' + (f'<p class="card-sub">{sub}</p>' if sub else ""),
        unsafe_allow_html=True,
    )


def legend(items):
    st.markdown(
        '<div class="legend">' + "".join(f'<span><i style="background:{c}"></i>{t}</span>' for t, c in items) + "</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- cabecera
h1, h2 = st.columns([5, 1.25], vertical_alignment="center")
with h1:
    st.markdown(
        f"""<div class="hdr"><img src="data:image/png;base64,{logo_b64()}" alt="UNIR"/><div class="sep"></div>
        <h1>Competencias en analítica: mercado vs. planes de estudio UNIR</h1>
        <span class="pill">PRELIMINAR</span>
        <span class="pill-sub">Cifras sujetas a validación oficial · relectura 30-oct-2026</span></div>""",
        unsafe_allow_html=True,
    )
with h2:
    with st.popover("Fuentes y notas", use_container_width=True):
        st.markdown(
            "**Aviso.** Cifras preliminares: relectura del 30-oct-2026 sobre 51 avisos completos "
            "(de 75; 24 ya no disponibles) y 29 planes (consulta aparte). Pendiente del clasificador y el juez oficiales. "
            "N de ofertas = 51, no 75.\n\n"
            "**Definiciones.** Explícita = nivel 2–3 · Aplicada = 3 · Parcial = 1 · Sin mención = 0 (propuesto).\n\n"
            "**No se usan** las columnas antiguas con N=75 ni uniones agrupadas recalculadas. "
            "«Toma de decisiones» es inestable y no se afirma como conclusión. P09 no se usa en conclusiones."
        )
        st.dataframe(
            notas.rename(columns={"campo": "Campo", "contenido": "Contenido"}),
            hide_index=True, height=260, use_container_width=True,
        )

t_res, t_comp, t_exp, t_enc = st.tabs(["Resumen", "Comparación", "Explorar", "Encuesta"])

# ================================================================ RESUMEN
with t_res:
    p = pivot("explicita")
    top_pos = p.sort_values("brecha", ascending=False).head(3)
    top_neg = p.sort_values("brecha").head(2)
    g = p.loc[p["brecha"].abs().idxmax()]

    insight = (
        "Las ofertas piden de forma explícita "
        + ", ".join(f"{corto(r.variable)} (+{r.brecha:.0f} pp)" for r in top_pos.itertuples())
        + " mucho más que los planes; los planes destacan en "
        + " y ".join(f"{corto(r.variable).lower()} ({r.brecha:.0f} pp)" for r in top_neg.itertuples())
        + "."
    )
    st.markdown(
        f'<p class="sec-h">¿Qué pide el mercado frente a lo que enseñan los planes?</p><p class="sec-i">{insight}</p>',
        unsafe_allow_html=True,
    )

    k = st.columns(4)
    kpis = [
        ("Ofertas analizadas", N_OF, "avisos completos (de 75)"),
        ("Planes de estudio", N_PL, "solo documentos; consulta aparte"),
        ("Respuestas de encuesta", N_ENC, "procesada el 14-oct-2026"),
        ("Variables", N_VAR, "4 categorías · preliminar"),
    ]
    for col, (lab, val, note) in zip(k, kpis):
        col.markdown(f'<div class="kpi"><div class="l">{lab}</div><div class="v">{val}</div><div class="n">{note}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([2.35, 1])
    with left:
        with st.container(key="card_res_main"):
            card_head("Mayores brechas · % con mención explícita (nivel 2–3)",
                      "8 variables con mayor diferencia entre ofertas y planes (solo documentos)")
            legend([(f"Ofertas (N={N_OF})", PURPLE), (f"Planes · documentos (N={N_PL})", BLUE)])
            top = p.reindex(p["brecha"].abs().sort_values(ascending=False).index).head(8)
            top = top.sort_values("brecha")  # positivo arriba
            fig = go.Figure()
            for f, col in [(F_PL, BLUE), (F_OF, PURPLE)]:
                fig.add_bar(
                    y=[corto(v) for v in top.variable], x=top[f], name=FUENTE_CORTA[f], orientation="h",
                    marker_color=col, text=[f"{x*100:.0f}%" for x in top[f]], textposition="outside",
                    cliponaxis=False, textfont=dict(size=13, color=INK),
                    customdata=top[f"ndn_{f}"], hovertemplate="%{y}: %{x:.1%} (%{customdata})<extra>" + FUENTE_CORTA[f] + "</extra>",
                )
            base_layout(fig, 336, barmode="group", bargap=0.28, bargroupgap=0.06, showlegend=False,
                        xaxis=dict(range=[0, 0.9], tickformat=".0%", dtick=0.2, gridcolor="#EEF0F4", tickfont=dict(size=12, color=MUTED), zeroline=False),
                        yaxis=dict(tickfont=dict(size=13.5), automargin=True))
            show(fig)
    with right:
        with st.container(key="card_res_big"):
            card_head("Brecha más grande")
            st.markdown(
                f"""<div class="big-l">{g.variable}</div>
                <div class="big">+{g.brecha:.0f} pp</div>
                <div class="row2"><span><i class="dot" style="background:{PURPLE}"></i>Ofertas</span><b>{g[F_OF]*100:.0f}% · {g[f'ndn_{F_OF}']}</b></div>
                <div class="bar"><div style="width:{g[F_OF]*100:.1f}%;background:{PURPLE}"></div></div>
                <div class="row2"><span><i class="dot" style="background:{BLUE}"></i>Planes (documentos)</span><b>{g[F_PL]*100:.0f}% · {g[f'ndn_{F_PL}']}</b></div>
                <div class="bar"><div style="width:{g[F_PL]*100:.1f}%;background:{BLUE}"></div></div>""",
                unsafe_allow_html=True,
            )
        with st.container(key="card_res_cov"):
            card_head("Cobertura de los datos")
            st.markdown(
                f"""<div class="row2"><span>Avisos completos recuperados</span><b>{N_OF} de 75 ({N_OF/75*100:.0f}%)</b></div>
                <div class="bar"><div style="width:{N_OF/75*100:.1f}%;background:{GREEN}"></div></div>
                <div class="row2"><span>Citas verificadas</span><b>{N_CITAS:,} de {N_CITAS:,}</b></div>
                <div class="bar"><div style="width:100%;background:{GREEN}"></div></div>
                <div class="row2"><span>Validación oficial (clasificador y juez)</span><b>pendiente</b></div>
                <div class="bar"><div style="width:0%"></div></div>""".replace(",", "."),
                unsafe_allow_html=True,
            )
    st.markdown('<p class="foot">Fuente: hoja UNIR_resultados_legible_v9 · relectura 30-oct-2026 · encuesta 14-oct-2026 · '
                'cifras preliminares, no usar como conclusiones definitivas.</p>', unsafe_allow_html=True)

# ================================================================ COMPARACIÓN
with t_comp:
    f1, f2, f3, f4 = st.columns([1.3, 1.3, 0.8, 2.6])
    cat = f1.selectbox("Categoría", ["Todas"] + CATEGORIAS, key="c_cat")
    med = f2.selectbox("Medida", list(MEDIDAS), format_func=MEDIDAS.get, key="c_med")
    topn = f3.selectbox("Mostrar", [8, 10, 12], index=1, format_func=lambda n: f"Top {n}", key="c_top")
    with f4:
        st.markdown(
            '<p class="sec-i" style="margin-top:1.55rem;">Planes = solo documentos. '
            '«Con consulta» solo existe para la medida explícita.</p>', unsafe_allow_html=True)

    pc = pivot(med, None if cat == "Todas" else cat)
    if pc.empty or "brecha" not in pc:
        st.info("No hay datos para esta selección.")
    else:
        sel = pc.reindex(pc["brecha"].abs().sort_values(ascending=False).index).head(topn).sort_values("brecha")
        ch = max(300, min(360, 30 * len(sel) + 40))
        a, b = st.columns([1.15, 1])
        with a:
            with st.container(key="card_c_gap"):
                card_head(f"Brecha en puntos porcentuales · {MEDIDAS[med]}",
                          "% Ofertas − % Planes (solo documentos). Positivo = más en ofertas.")
                cols = [PURPLE if v >= 0 else BLUE for v in sel.brecha]
                fig = go.Figure(go.Bar(
                    y=[corto(v) for v in sel.variable], x=sel.brecha, orientation="h", marker_color=cols,
                    text=[f"{v:+.0f} pp" for v in sel.brecha], textposition="outside", cliponaxis=False,
                    textfont=dict(size=13, color=INK), hovertemplate="%{y}: %{x:+.1f} pp<extra></extra>"))
                lim = max(20, sel.brecha.abs().max() * 1.3)
                base_layout(fig, ch, showlegend=False,
                            xaxis=dict(range=[-lim, lim], ticksuffix=" pp", gridcolor="#EEF0F4", zerolinecolor="#9CA3AF",
                                       tickfont=dict(size=12, color=MUTED)),
                            yaxis=dict(tickfont=dict(size=13.5), automargin=True))
                show(fig)
        with b:
            with st.container(key="card_c_dot"):
                srcs = [F_OF, F_PL] + ([F_PC] if med == "explicita" else [])
                card_head(f"Ofertas vs. planes · {MEDIDAS[med]}", "Porcentaje de cada fuente para las mismas variables")
                legend([(FUENTE_CORTA[s], FUENTE_COLOR[s]) for s in srcs])
                fig = go.Figure()
                ylab = [corto(v) for v in sel.variable]
                for _, r in sel.iterrows():
                    vals = [r[s] for s in srcs if pd.notna(r.get(s))]
                    fig.add_scatter(x=[min(vals), max(vals)], y=[corto(r.variable)] * 2, mode="lines",
                                    line=dict(color="#D1D5DB", width=3), hoverinfo="skip", showlegend=False)
                for s in srcs:
                    fig.add_scatter(
                        x=sel[s], y=ylab, mode="markers+text" if s != F_PC else "markers", name=FUENTE_CORTA[s],
                        marker=dict(color=FUENTE_COLOR[s], size=12 if s != F_PC else 9,
                                    symbol="circle" if s != F_PC else "diamond", line=dict(color="white", width=1.5)),
                        text=[f"{x*100:.0f}%" for x in sel[s]] if s != F_PC else None,
                        textposition=["middle right" if r[F_OF] >= r[F_PL] else "middle left" for _, r in sel.iterrows()] if s == F_OF
                        else ["middle left" if r[F_OF] >= r[F_PL] else "middle right" for _, r in sel.iterrows()],
                        textfont=dict(size=12.5, color=FUENTE_COLOR[s] if s != F_PL else "#1F6FA8"),
                        customdata=sel[f"ndn_{s}"],
                        hovertemplate="%{y}: %{x:.1%} (%{customdata})<extra>" + FUENTE_CORTA[s] + "</extra>")
                base_layout(fig, ch - 22, showlegend=False,
                            xaxis=dict(range=[-0.12, 1.0], tickformat=".0%", dtick=0.25, gridcolor="#EEF0F4",
                                       tickfont=dict(size=12, color=MUTED), zeroline=False),
                            yaxis=dict(tickfont=dict(size=13.5), automargin=True, showgrid=False))
                show(fig)
        ex = pc.reindex(pc["brecha"].abs().sort_values(ascending=False).index).head(topn)
        with st.expander(f"Ver tabla exacta (n de N) de estas {len(ex)} variables"):
            t = ex[["variable", "categoria", f"ndn_{F_OF}", f"ndn_{F_PL}", "brecha"]].rename(columns={
                "variable": "Variable", "categoria": "Categoría", f"ndn_{F_OF}": "Ofertas (n de N)",
                f"ndn_{F_PL}": "Planes docs (n de N)", "brecha": "Brecha (pp)"})
            st.dataframe(t, hide_index=True, height=200, use_container_width=True,
                         column_config={"Brecha (pp)": st.column_config.NumberColumn(format="%+.1f")})
        if "Toma de decisiones" in set(sel.variable):
            st.markdown('<p class="foot">«Toma de decisiones»: variable inestable, pendiente de re-juzgamiento; no se afirma como conclusión.</p>',
                        unsafe_allow_html=True)

# ================================================================ EXPLORAR
with t_exp:
    e1, e2, e3, e4 = st.columns([1.1, 1.5, 1.4, 2.0])
    fu = e1.selectbox("Fuente", ["Ofertas", "Planes de estudio"], key="e_fu")
    ids = sorted(det.loc[det.fuente == fu, "id"].unique())
    uid = e2.selectbox("Oferta o programa", ["Todas"] + ids, key="e_id",
                       format_func=lambda x: f"Todas ({len(ids)})" if x == "Todas" else x)
    ecat = e3.selectbox("Categoría", ["Todas"] + CATEGORIAS, key="e_cat")
    d = det[det.fuente == fu]
    if uid != "Todas":
        d = d[d.id == uid]
    if ecat != "Todas":
        d = d[d.categoria == ecat]
    with e4:
        n_exp = int(d.presencia_explicita.sum())
        st.markdown(
            f'<p class="sec-i" style="margin-top:1.55rem;"><b>{d.id.nunique()}</b> unidad(es) · <b>{d.variable.nunique()}</b> variables · '
            f'<b>{n_exp}</b> de {len(d)} registros con mención explícita (nivel 2–3).</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([0.95, 1.15, 1.9])
    cnt = d.nivel.value_counts().reindex([3, 2, 1, 0], fill_value=0)
    with c1:
        with st.container(key="card_e_donut"):
            card_head("Distribución de niveles", "Registros variable × unidad")
            fig = go.Figure(go.Pie(
                labels=[l for _, l, _ in NIVELES], values=[int(cnt[n]) for n, _, _ in NIVELES],
                marker=dict(colors=[c for _, _, c in NIVELES], line=dict(color="white", width=2)),
                hole=0.62, sort=False, direction="clockwise", texttemplate="%{percent:.0%}",
                textfont=dict(size=12.5), insidetextfont=dict(color="white"),
                hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"))
            fig.add_annotation(text=f"<b>{(cnt[2]+cnt[3])/max(1,len(d))*100:.0f}%</b><br><span style='font-size:12px;color:{MUTED}'>explícita</span>",
                               showarrow=False, font=dict(size=22, color=INK))
            base_layout(fig, 236, showlegend=False, margin=dict(l=4, r=4, t=4, b=4))
            show(fig)
            legend([(l, c) for _, l, c in NIVELES])
    with c2:
        with st.container(key="card_e_stack"):
            card_head("Niveles por categoría", "% de registros en cada nivel (100 %)")
            ct = d.groupby(["categoria", "nivel"]).size().unstack(fill_value=0).reindex(columns=[3, 2, 1, 0], fill_value=0)
            ct = ct.reindex([c for c in reversed(CATEGORIAS) if c in ct.index])
            pct = ct.div(ct.sum(axis=1), axis=0)
            fig = go.Figure()
            for n, l, c in NIVELES:
                fig.add_bar(y=[x.replace("Habilidades ", "H. ") for x in pct.index], x=pct[n], name=l, orientation="h",
                            marker=dict(color=c, line=dict(color="white", width=1)),
                            text=[f"{v*100:.0f}%" if v >= 0.14 else "" for v in pct[n]], textposition="inside", textangle=0,
                            insidetextanchor="middle", textfont=dict(size=12, color="white" if n else INK),
                            customdata=ct[n], hovertemplate="%{y} · " + l + ": %{x:.0%} (%{customdata})<extra></extra>")
            base_layout(fig, 286, barmode="stack", bargap=0.35, showlegend=False,
                        xaxis=dict(range=[0, 1], tickformat=".0%", dtick=0.25, gridcolor="#EEF0F4", tickfont=dict(size=12, color=MUTED)),
                        yaxis=dict(tickfont=dict(size=13), automargin=True))
            show(fig)
    with c3:
        with st.container(key="card_e_tbl"):
            solo = st.toggle("Solo registros con evidencia (nivel 1–3)", value=True, key="e_solo")
            tt = d[d.nivel >= 1] if solo else d
            tt = tt.sort_values(["nivel", "id", "variable"], ascending=[False, True, True])
            cols = ["id", "variable", "nivel", "cita_corta", "ubicacion"]
            ren = {"id": "ID", "variable": "Variable", "nivel": "Nivel", "cita_corta": "Cita literal", "ubicacion": "Ubicación"}
            if fu == "Planes de estudio":
                cols += ["nivel_con_consulta", "cita_consulta_corta"]
                ren.update({"nivel_con_consulta": "Nivel c/ consulta", "cita_consulta_corta": "Cita consulta"})
            st.dataframe(
                tt[cols].rename(columns=ren), hide_index=True, height=262, use_container_width=True,
                column_config={
                    "ID": st.column_config.TextColumn(width="small"),
                    "Variable": st.column_config.TextColumn(width="small"),
                    "Nivel": st.column_config.NumberColumn(width="small", format="%d"),
                    "Cita literal": st.column_config.TextColumn(width="large"),
                    "Nivel c/ consulta": st.column_config.NumberColumn(format="%d"),
                },
            )
            st.markdown(f'<p class="card-sub">{len(tt):,} registros · desplaza dentro de la tabla · citas recortadas a ~220 caracteres</p>'.replace(",", "."),
                        unsafe_allow_html=True)

# ================================================================ ENCUESTA
with t_enc:
    meta = enc[["pregunta", "texto_pregunta", "n_respuestas_validas", "N_formulario"]].drop_duplicates("pregunta")
    graf = [q for q in meta.pregunta if q != "P10"]
    a, b = st.columns([2.35, 1])
    with a:
        q = st.selectbox("Pregunta", graf, key="q_sel",
                         format_func=lambda x: f"{x} · {meta.set_index('pregunta').loc[x, 'texto_pregunta']}" + (" · PENDIENTE" if x in ("P04", "P09") else ""))
        s = enc[enc.pregunta == q].copy()
        if q in ("P05", "P07", "P09"):
            s["o"] = pd.to_numeric(s.opcion, errors="coerce")
            s = s.sort_values("o", ascending=False)
        else:
            s = s.sort_values("porcentaje").tail(9)
        with st.container(key="card_q_chart"):
            pend = q in ("P04", "P09")
            card_head(("⚠ PENDIENTE · " if pend else "") + meta.set_index("pregunta").loc[q, "texto_pregunta"],
                      f"{int(s.N.max())} respuestas válidas" + (" · solo opciones más frecuentes" if len(enc[enc.pregunta == q]) > 9 else ""))
            fig = go.Figure(go.Bar(
                y=[str(o) if len(str(o)) <= 34 else str(o)[:32] + "…" for o in s.opcion], x=s.porcentaje, orientation="h",
                marker_color="#C9A227" if pend else PURPLE,
                text=[f"{p*100:.0f}% ({int(n)} de {int(N)})" for p, n, N in zip(s.porcentaje, s.n, s.N)],
                textposition="outside", cliponaxis=False, textfont=dict(size=13, color=INK),
                hovertemplate="%{y}: %{x:.1%}<extra></extra>"))
            base_layout(fig, 300, showlegend=False,
                        xaxis=dict(range=[0, max(0.4, s.porcentaje.max() * 1.45)], tickformat=".0%", gridcolor="#EEF0F4", tickfont=dict(size=12, color=MUTED)),
                        yaxis=dict(tickfont=dict(size=13), automargin=True))
            show(fig)
    with b:
        with st.container(key="card_q_flags"):
            card_head("Estado de las preguntas")
            st.markdown(
                f"""<div class="flag"><span class="tag p">P04 · PENDIENTE</span>Falta la regla para respuestas con ≠ 3 opciones.</div>
                <div class="flag"><span class="tag p">P09 · PENDIENTE</span>Escala por verificar (1 a 8). <b>No usar en conclusiones.</b></div>
                <div class="flag"><span class="tag o">P10 · ABIERTA</span>45 de 54 respuestas en texto libre, sin codificar; no se grafica.</div>
                <div class="flag"><span class="tag o">RESTO</span>Procesadas el 14-oct-2026, sin IA; sin cambios el 30-oct.</div>""",
                unsafe_allow_html=True,
            )
        with st.container(key="card_q_kpi"):
            card_head("Respuestas del formulario")
            st.markdown(f'<div class="big">{N_ENC}</div><p class="card-sub">Bloque separado de los niveles 0–3 de ofertas y planes.</p>',
                        unsafe_allow_html=True)
