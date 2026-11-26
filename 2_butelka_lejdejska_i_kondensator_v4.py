# -*- coding: utf-8 -*-
"""Butelka lejdejska i kondensator, aplikacja dydaktyczna Streamlit.
Uruchomienie: streamlit run butelka_lejdejska_i_kondensator_v4.py
"""
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.html("""
    <style>
    /* Powiększenie tekstu etykiety w st.metric */
    [data-testid="stMetricLabel"] div p {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    /* Opcjonalnie: Powiększenie samej ikony pytajnika (tooltipu), aby pasowała do tekstu */
    [data-testid="stMetricLabel"] button {
        transform: scale(1.3);
        margin-left: 8px !important;
    }
    </style>
""")

st.set_page_config(page_title="Butelka lejdejska i kondensator", page_icon="⚡", layout="wide")
EPS0 = 8.8541878128e-12
GLASS_EPS_R = 5.0
MATERIALS = {
    "Powietrze": (1.0006, "#bae6fd"), "Szkło": (5.0, "#a7f3d0"),
    "Papier": (3.5, "#fde68a"), "Tworzywo": (2.5, "#ddd6fe"),
    "Ceramika": (9.0, "#fed7aa")}

def eng(v, unit):
    if not np.isfinite(v): return "∞"
    if v == 0: return f"0 {unit}"
    for k,p in [(1e9,"G"),(1e6,"M"),(1e3,"k"),(1,""),(1e-3,"m"),(1e-6,"µ"),(1e-9,"n"),(1e-12,"p")]:
        if abs(v) >= k: return f"{v/k:.4g} {p}{unit}"
    return f"{v:.3e} {unit}"

def dots(fig, x, ys, positive, size=14):
    color, char = ("#ef4444", "+") if positive else ("#38bdf8", "−")
    fig.add_trace(go.Scatter(x=[x]*len(ys), y=ys, mode="markers+text",
        marker=dict(size=size, color=color, line=dict(color="white",width=1)),
        text=[char]*len(ys), textposition="middle center", textfont=dict(color="white",size=10),
        hovertemplate=("ładunek dodatni" if positive else "elektron")+"<extra></extra>", showlegend=False))

def bound_column(fig, x_negative, x_positive, ys):
    """Dipole poziome: od końca ujemnego do dodatniego."""
    for y in ys:
        fig.add_shape(type="line",x0=x_negative,y0=y,x1=x_positive,y1=y,line=dict(color="#e2e8f0",width=2))
    dots(fig,x_negative,ys,False,10); dots(fig,x_positive,ys,True,10)

def base_figure(voltage, charge):
    fig=go.Figure()
    fig.update_xaxes(range=[0,10],visible=False,fixedrange=True)
    fig.update_yaxes(range=[0,7],visible=False,fixedrange=True,scaleanchor="x",scaleratio=1)
    fig.update_layout(height=590,margin=dict(l=5,r=5,t=55,b=35),paper_bgcolor="#07111f",
        plot_bgcolor="#0f2035",showlegend=False,
        title=dict(text=f"u = {voltage:.2f} V   |   q = {eng(charge,'C')}",x=.5,
                   font=dict(color="#facc15",size=18)))
    return fig

def jar_visualization(voltage, charge):
    """Osiowo symetryczny przekrój. Ładunki swobodne są rysowane ponad elektrodami."""
    fig = base_figure(voltage, charge)
    active = abs(voltage) > 1e-12
    inner_positive = voltage >= 0
    n = int(np.clip(4 + 2*np.log10(1 + abs(charge)*1e12), 4, 11)) if active else 0
    ys = np.linspace(1.45, 5.05, n) if n else np.array([])

    # Najpierw geometria, potem dipole, a na końcu ładunki swobodne.
    for x0, x1 in [(2.30, 2.68), (7.32, 7.70)]:
        fig.add_shape(type="rect", x0=x0, y0=1.10, x1=x1, y1=5.35,
                      fillcolor="#94a3b8", line=dict(color="white", width=1), layer="below")
    for x0, x1 in [(2.68, 3.48), (6.52, 7.32)]:
        fig.add_shape(type="rect", x0=x0, y0=.95, x1=x1, y1=5.65,
                      fillcolor="rgba(167,243,208,.30)", line=dict(color="#a7f3d0", width=5), layer="below")
    fig.add_shape(type="rect", x0=3.48, y0=1.15, x1=6.52, y1=5.15,
                  fillcolor="#64748b", line=dict(color="#cbd5e1", width=2), layer="below")
    fig.add_shape(type="line", x0=5, y0=5.15, x1=5, y1=6.25,
                  line=dict(color="#d1d5db", width=8), layer="below")
    fig.add_trace(go.Scatter(x=[5], y=[6.34], mode="markers",
                             marker=dict(size=28, color="#d1d5db"), hoverinfo="skip", showlegend=False))

    if active:
        # Ujemny koniec dipola jest zwrócony ku dodatniej elektrodzie.
        # Gdy wnętrze jest dodatnie: lewy dipol ma + po lewej i − po prawej,
        # prawy dipol ma − po lewej i + po prawej.
        if inner_positive:
            bound_column(fig, 3.30, 2.86, ys)  # lewy pas szkła: + ... −
            bound_column(fig, 6.70, 7.14, ys)  # prawy pas szkła: − ... +
        else:
            bound_column(fig, 2.86, 3.30, ys)
            bound_column(fig, 7.14, 6.70, ys)

        # Ładunki na powierzchniach metalu graniczących ze szkłem.
        # Pozycje znajdują się nieco w szkle, dzięki czemu symbole nie są zasłaniane.
        dots(fig, 2.54, ys, not inner_positive, 20)
        dots(fig, 3.70, ys, inner_positive, 20)
        dots(fig, 6.30, ys, inner_positive, 20)
        dots(fig, 7.46, ys, not inner_positive, 20)

    labels = [
        (5, 5.42, "okładzina        wewnętrzna"),
        (1.78, .28, "okładzina zewnętrzna"),
        (8.22, .28, "okładzina zewnętrzna"),
        (3.08, .62, "szkło"), (6.92, .62, "szkło")]
    for x, y, text in labels:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                           font=dict(color="#e5e7eb", size=13))
    fig.add_annotation(x=5, y=6.77, text="przekrój osiowo symetryczny",
                       showarrow=False, font=dict(color="#a7f3d0", size=12))
    return fig


def plate_visualization(voltage, charge, color):
    fig = base_figure(voltage, charge)
    active = abs(voltage) > 1e-12
    left_positive = voltage >= 0
    n = int(np.clip(5 + 2*np.log10(1 + abs(charge)*1e12), 5, 13)) if active else 0
    ys = np.linspace(1.30, 5.45, n) if n else np.array([])

    fig.add_shape(type="rect", x0=2.20, y0=.95, x1=2.62, y1=5.80,
                  fillcolor="#d1d5db", line=dict(color="white", width=1), layer="below")
    fig.add_shape(type="rect", x0=7.38, y0=.95, x1=7.80, y1=5.80,
                  fillcolor="#d1d5db", line=dict(color="white", width=1), layer="below")
    fig.add_shape(type="rect", x0=2.62, y0=.95, x1=7.38, y1=5.80,
                  fillcolor=color, opacity=.25, line=dict(color=color, width=1), layer="below")

    if active:
        dipole_ys = np.linspace(1.55, 5.20, 4)
        for x in np.linspace(3.15, 6.85, 5):
            # E w prawo: lewa elektroda dodatnia, więc ujemny koniec dipola po lewej.
            if left_positive:
                bound_column(fig, x-.17, x+.17, dipole_ys)
            else:
                bound_column(fig, x+.17, x-.17, dipole_ys)

        # Symbole wystają do obszaru dielektryka i są rysowane po wszystkich kształtach.
        dots(fig, 2.68, ys, left_positive, 20)
        dots(fig, 7.32, ys, not left_positive, 20)
        xa, xb = (3.0, 7.0) if left_positive else (7.0, 3.0)
        fig.add_annotation(x=xb, y=6.20, ax=xa, ay=6.20, xref="x", yref="y",
                           axref="x", ayref="y", text="", showarrow=True,
                           arrowhead=3, arrowwidth=3, arrowcolor="#d8b4fe")

    for x, y, text, c in [(2.41,.62,"elektroda 1","white"),
                           (7.59,.62,"elektroda 2","white"),
                           (5,.28,"dielektryk",color),
                           (5,6.52,"pole elektryczne E" if active else "E = 0","#d8b4fe")]:
        fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                           font=dict(color=c, size=14))
    return fig

def show_legend():
    st.markdown("🔴 **ładunek dodatni** &nbsp;&nbsp; 🔵 **elektron / ładunek ujemny** &nbsp;&nbsp; 🔵−🔴 **dipol dielektryka**")

st.title("⚡ Butelka lejdejska i kondensator")
st.markdown("#### Interaktywny model dla studentów II roku")
with st.sidebar:
    st.header("Ustawienia modelu")
    mode=st.selectbox("Układ",["Butelka lejdejska","Kondensator płaski, napięcie stałe","Kondensator płaski, napięcie przemienne"],help="Wybierz historyczny kondensator albo kondensator płaski zasilany DC lub AC.")
    jar=mode=="Butelka lejdejska"
    if jar:
        st.text_input("Dielektryk",value="Szkło",disabled=True,help="W klasycznej butelce lejdejskiej ścianka szklana jest dielektrykiem.")
        epsr=GLASS_EPS_R; color=MATERIALS["Szkło"][1]
        st.caption("Do obliczeń przyjęto εr szkła = 5,0.")
        rcm=st.slider("Promień okładziny [cm]",2.,12.,5.,.5,help="Promień cylindrycznej części okładziny.")
        hcm=st.slider("Wysokość okładzin [cm]",5.,30.,15.,.5,help="Wspólna wysokość obu okładzin.")
        dmm=st.slider("Grubość szkła [mm]",.5,6.,2.,.1,help="Odległość promieniowa między okładzinami.")
        C=2*math.pi*EPS0*epsr*(hcm/100)/math.log((rcm/100+dmm/1000)/(rcm/100))
    else:
        mat=st.selectbox("Dielektryk",list(MATERIALS),help="Izolator między elektrodami.")
        default_eps,color=MATERIALS[mat]
        epsr=st.slider("Względna przenikalność εr",1.,15.,float(default_eps),.1,help="Im większa εr, tym większa pojemność.")
        acm2=st.slider("Pole jednej elektrody [cm²]",10.,1000.,200.,10.,help="Pole wspólnej powierzchni elektrod.")
        dmm=st.slider("Odległość elektrod [mm]",.1,10.,1.,.1,help="Mniejsza odległość zwiększa pojemność.")
        C=EPS0*epsr*acm2*1e-4/(dmm*1e-3)
    Umax=st.slider("Napięcie źródła [V]",0.,500.,100.,5.,help="Dla AC jest to amplituda napięcia.")
    ac=mode.endswith("przemienne")
    if ac:
        f=st.slider("Częstotliwość [Hz]",.1,200.,50.,.1,help="Liczba okresów na sekundę.")
        phase=st.slider("Faza obserwacji [°]",0,360,45,1,help="Chwila obserwacji w okresie.")
        phi=math.radians(phase); U=Umax*math.sin(phi); omega=2*math.pi*f; Im=omega*C*Umax; I=Im*math.cos(phi); Xc=1/(omega*C)
    else:
        f=0.; pct=st.slider("Stopień naładowania [%]",0,100,100,1,help="Umowny etap ładowania.")
        U=Umax*pct/100; I=Im=0.; Xc=math.inf
    st.warning("Model dydaktyczny. Nie wykonuj doświadczeń wysokonapięciowych poza wyposażonym laboratorium.")
Q=C*U; W=.5*C*U**2; E=U/(dmm*1e-3)
for col,label,val,h in zip(st.columns(4),["Pojemność C","Napięcie chwilowe U","Ładunek q = C⋅U","Energia W = ½⋅C⋅u²"],[eng(C,"F"),eng(U,"V"),eng(Q,"C"),eng(W,"J")],["Zdolność magazynowania ładunku.","Różnica potencjałów.","Wartość ładunku każdej elektrody.","Energia pola elektrycznego."]): col.metric(label,val,help=h)
left,right=st.columns([5,2],gap="large")
with left:
    st.subheader("Model pola, ładunku i polaryzacji")
    show_legend(); fig=jar_visualization(U,Q) if jar else plate_visualization(U,Q,color)
    st.plotly_chart(fig,width='stretch',config={"displaylogo":False})
with right:
    st.subheader("Jak czytać widok?")
    if jar: st.markdown("Przekrój jest **osiowo symetryczny**. Obie jasnoszare części należą do jednej okładziny zewnętrznej, a środkowy obszar do jednej okładziny wewnętrznej. Dwa zielone pasy są przekrojami tej samej szklanej ścianki.")
    else: st.markdown("Duże symbole ładunku znajdują się na powierzchniach elektrod zwróconych ku dielektrykowi. Przy zmianie znaku napięcia znaki elektrod i orientacja dipoli odwracają się.")
    st.metric("Natężenie pola |E|",eng(abs(E),"V/m"),help="W przybliżeniu |E|=|u|/d.")

st.subheader("Przebiegi elektryczne")
if ac:
    t=np.linspace(0,2/f,600); u=Umax*np.sin(2*np.pi*f*t); i=Im*np.cos(2*np.pi*f*t)
    g=go.Figure(); g.add_scatter(x=t*1000,y=u,name="napięcie"); g.add_scatter(x=t*1000,y=i/Im*Umax if Im else i,name="natężenie prądu",line=dict(dash="dash")); g.update_layout(height=380,xaxis_title="czas [ms]")
    st.plotly_chart(g,width='stretch',config={"displaylogo":False})
    # a,b,c=st.columns(3); a.metric("Amplituda prądu",eng(Im,"A")); b.metric("Reaktancja XC",eng(Xc,"Ω")); c.metric("Przesunięcie fazowe","+90°")
else:
    z=np.linspace(0,5,500); g=go.Figure(); g.add_scatter(x=z,y=Umax*(1-np.exp(-z)),name="napięcie"); g.add_scatter(x=z,y=Umax*np.exp(-z),name="natężenie prądu",line=dict(dash="dash")); g.update_layout(height=380,xaxis_title="czas t/τ")
    st.plotly_chart(g,width='stretch',config={"displaylogo":False})
    st.caption("Dla ładowania przez rezystor napięcie rośnie, a prąd maleje. Stała czasowa τ=RC.")
with st.expander("Najważniejsze pojęcia:"):
    st.markdown(r"""**Pojemność:** \(C=Q/U\).   
**Butelka lejdejska:** historyczny kondensator, w którym szkło oddziela okładzinę wewnętrzną od zewnętrznej.  
**Polaryzacja:** związane ładunki dielektryka ustawiają się przeciwnie do pola; przy elektrodzie dodatniej pojawia się strona ujemna dipolu.  
""")

