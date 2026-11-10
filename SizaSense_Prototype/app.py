import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium

# Try loading custom engine functions, with robust fallbacks
try:
    from engine.risk import score_service, risk_label, action_for
except ImportError:
    def score_service(row):
        # Fallback scoring if engine file is missing
        return min(100, int(row.get('flood_exposure', 20)*0.4 + row.get('heat_exposure', 20)*0.4 + row.get('access_vulnerability', 20)*0.2))
    def risk_label(score):
        if score >= 75: return "Critical"
        if score >= 60: return "High"
        if score >= 40: return "Moderate"
        return "Low"
    def action_for(row):
        lbl = risk_label(score_service(row))
        if lbl in ["Critical", "High"]:
            return "Deploy immediate WASH field inspection team & maternal referral pathway check."
        elif lbl == "Moderate":
            return "Monitor satellite environmental signals & schedule routine community follow-up."
        return "Maintain routine baseline surveillance."

# Page Setup & Metadata
st.set_page_config(
    page_title="SizaSense | Environmental & WASH Resilience Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Custom CSS Styling
st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; max-width: 1450px; }
    .hero-banner {
        padding: 1.8rem 2rem;
        border-radius: 16px;
        background: linear-gradient(125deg, #0d2f38 0%, #154c46 50%, #1b6357 100%);
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .hero-tag {
        letter-spacing: 0.18em;
        font-size: 0.78rem;
        color: #7de3c8;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 0.4rem 0;
    }
    .hero-desc {
        color: #d1ece4;
        font-size: 1.05rem;
        max-width: 900px;
        margin: 0;
    }
    .dpg-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        color: #ffffff;
        margin-top: 0.8rem;
    }
    [data-testid="stMetric"] {
        background: #f4f8f6;
        border: 1px solid #d4e4df;
        padding: 14px 16px;
        border-radius: 14px;
    }
    .info-card {
        background: #f8faf9;
        border-left: 4px solid #1b6357;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>

<div class="hero-banner">
    <div class="hero-tag">SUMMERNET GROUP · SIZASENSE OPEN INITIATIVE</div>
    <h1 class="hero-title">SizaSense Resilience Intelligence</h1>
    <p class="hero-desc">Open-source Digital Public Good decision support combining Earth Observation (EO) environmental exposure indices, community WASH signals, and maternal healthcare accessibility monitoring.</p>
    <div class="dpg-badge">UNICEF Digital Public Goods Framework Compliant · MIT Licensed</div>
</div>
""", unsafe_allow_html=True if hasattr(st, "unsafe_unsafe_html") else True)

# Data Loader with Automated Synthetic Fallbacks
@st.cache_data
def load_data():
    try:
        sites_df = pd.read_csv("data/demo_services.csv")
    except Exception:
        sites_df = pd.DataFrame([
            {"site_name": "Mdantsane NU2 Clinic", "service_type": "Maternal & Primary Health", "area": "Mdantsane", "latitude": -32.960, "longitude": 27.730, "flood_exposure": 78, "heat_exposure": 42, "access_vulnerability": 80},
            {"site_name": "Duncan Village Health Centre", "service_type": "Primary Healthcare", "area": "East London Central", "latitude": -33.015, "longitude": 27.885, "flood_exposure": 85, "heat_exposure": 65, "access_vulnerability": 75},
            {"site_name": "Frere Maternal Care Unit", "service_type": "Referral Hospital", "area": "East London Central", "latitude": -33.003, "longitude": 27.892, "flood_exposure": 25, "heat_exposure": 30, "access_vulnerability": 20},
            {"site_name": "Cambridge Community Clinic", "service_type": "Community Clinic", "area": "Cambridge", "latitude": -32.978, "longitude": 27.881, "flood_exposure": 40, "heat_exposure": 55, "access_vulnerability": 35},
            {"site_name": "Quigney Outreach Point", "service_type": "Mobile Health Stop", "area": "Quigney", "latitude": -33.018, "longitude": 27.915, "flood_exposure": 60, "heat_exposure": 45, "access_vulnerability": 50},
        ])

    try:
        water_df = pd.read_csv("data/demo_water_observations.csv")
    except Exception:
        water_df = pd.DataFrame([
            {"water_point": "Mdantsane Stream Crossing", "area": "Mdantsane", "reported_date": "2026-11-01", "reported_concern": 75, "verification_status": "Community Signal", "notes": "High turbidity post-rain"},
            {"water_point": "Duncan Village Standpipe B", "area": "East London Central", "reported_date": "2026-11-04", "reported_concern": 82, "verification_status": "Field Verified", "notes": "Pressure drop & low flow"},
            {"water_point": "Nahoon River Intake Spot", "area": "Cambridge", "reported_date": "2026-11-05", "reported_concern": 30, "verification_status": "Baseline Normal", "notes": "Normal visual clarity"},
        ])
    return sites_df, water_df

sites_raw, water_raw = load_data()

# Process Scores
sites = sites_raw.copy()
if "risk_score" not in sites.columns:
    sites["risk_score"] = sites.apply(score_service, axis=1)
if "risk_level" not in sites.columns:
    sites["risk_level"] = sites.risk_score.apply(risk_label)
if "action" not in sites.columns:
    sites["action"] = sites.apply(action_for, axis=1)

# Sidebar Controls
st.sidebar.title("SizaSense Controls")
st.sidebar.caption("Demonstration Platform · Eastern Cape Region")

selected_area = st.sidebar.selectbox("Filter Geographical Area", ["All Areas"] + sorted(sites["area"].unique().tolist()))
if selected_area != "All Areas":
    filtered_sites = sites[sites["area"] == selected_area].copy()
    filtered_water = water_raw[water_raw["area"] == selected_area].copy()
else:
    filtered_sites = sites.copy()
    filtered_water = water_raw.copy()

st.sidebar.markdown("---")
st.sidebar.markdown("**System Governance**")
st.sidebar.info("SizaSense operates under MIT License with strict NOTICE trademark protection. No commercial mining data or patient PII is stored.")

# Core Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Monitored Facilities", len(filtered_sites))
m2.metric("Critical / High Exposure", int(filtered_sites["risk_level"].isin(["High", "Critical"]).sum()))
m3.metric("WASH Observations", len(filtered_water))
m4.metric("Priority Action Queue", int((filtered_sites["risk_score"] >= 60).sum()))

st.markdown("<p style='font-size:0.82rem; color:#666;'><i>* Note: Indicators represent decision-support signals derived from synthetic models and environmental proxies. Human field verification is strictly required before intervention.</i></p>", unsafe_allow_html=True)
st.divider()

# Primary Tabs Layout
tab_overview, tab_pulse, tab_lens, tab_queue, tab_governance = st.tabs([
    "📍 Environmental Map & Overview",
    "🩺 SizaPulse (Services)",
    "💧 SizaLens (WASH)",
    "🚨 Priority Queue",
    "🛡️ Governance & Compliance"
])

# TAB 1: OVERVIEW & MAP
with tab_overview:
    col_map, col_chart = st.columns([1.7, 1])
    
    with col_map:
        st.subheader("Spatial Environmental Risk Map")
        st.caption("Interactive Leaflet/Folium map rendering risk hotspots without external API key dependencies.")
        
        # Center map dynamically
        avg_lat = filtered_sites["latitude"].mean() if not filtered_sites.empty else -32.98
        avg_lon = filtered_sites["longitude"].mean() if not filtered_sites.empty else 27.85
        
        # Open-access map tiles (CartoDB Positron with OpenStreetMap fallback - NO API KEY NEEDED)
        m = folium.Map(location=[-32.9365, 27.9116], zoom_start=12, tiles="OpenStreetMap")
        
        color_map = {"Low": "#28a745", "Moderate": "#ffc107", "High": "#fd7e14", "Critical": "#dc3545"}
        
        for _, r in filtered_sites.iterrows():
            score = r["risk_score"]
            level = r["risk_level"]
            folium.CircleMarker(
                location=[r["latitude"], r["longitude"]],
                radius=9 + (score / 15),
                color=color_map.get(level, "#6c757d"),
                fill=True,
                fill_color=color_map.get(level, "#6c757d"),
                fill_opacity=0.75,
                tooltip=f"<b>{r['site_name']}</b><br>Score: {score}/100 ({level})",
                popup=f"""
                <div style='font-family:sans-serif; width:220px;'>
                    <h4 style='margin:0 0 5px 0;'>{r['site_name']}</h4>
                    <b>Category:</b> {r['service_type']}<br>
                    <b>Area:</b> {r['area']}<br>
                    <b>Risk Score:</b> {score}/100<br>
                    <hr style='margin:8px 0;'>
                    <small><b>Recommended Action:</b><br>{r['action']}</small>
                </div>
                """
            ).add_to(m)
        
        st_folium(m, height=480, width=None, use_container_width=True, returned_objects=[])

    with col_chart:
        st.subheader("Risk Score Distribution")
        st.caption("Categorical breakdown across facility sites.")
        
        counts = filtered_sites["risk_level"].value_counts().reindex(["Critical", "High", "Moderate", "Low"]).fillna(0).reset_index()
        counts.columns = ["Risk Level", "Facility Count"]
        
        fig_bar = px.bar(
            counts, 
            x="Risk Level", 
            y="Facility Count", 
            color="Risk Level",
            color_discrete_map={"Low": "#28a745", "Moderate": "#ffc107", "High": "#fd7e14", "Critical": "#dc3545"},
            text_auto=True
        )
        fig_bar.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=340)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("""
        <div class="info-card">
            <b>Interpretation Protocol:</b><br>
            Facilities categorized as <b>High</b> or <b>Critical</b> represent priority zones for infrastructure validation, emergency power backup checks, and local health pathway continuity.
        </div>
        """, unsafe_allow_html=True)

# TAB 2: SIZAPULSE (SERVICES)
with tab_pulse:
    st.subheader("SizaPulse · Essential Health & Maternal Facility Resilience")
    st.write("Examine environmental exposure and physical accessibility factors affecting community facilities.")
    
    st.dataframe(
        filtered_sites[["site_name", "service_type", "area", "risk_score", "risk_level", "action"]].sort_values("risk_score", ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.subheader("Individual Facility Exposure Drilldown")
    chosen_site = st.selectbox("Select facility for in-depth diagnostic:", filtered_sites["site_name"].tolist())
    
    if chosen_site:
        row = filtered_sites[filtered_sites["site_name"] == chosen_site].iloc[0]
        
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Overall Risk Score", f"{row['risk_score']} / 100")
        d2.metric("Flood Exposure Index", f"{row.get('flood_exposure', 'N/A')} / 100")
        d3.metric("Heat Stress Anomaly", f"{row.get('heat_exposure', 'N/A')} / 100")
        d4.metric("Access Vulnerability", f"{row.get('access_vulnerability', 'N/A')} / 100")
        
        st.info(f"**Action Recommendation:** {row['action']}")

# TAB 3: SIZALENS (WASH)
with tab_lens:
    st.subheader("SizaLens · Water & WASH Sentinel Intelligence")
    st.write("Track surface water observations, community reports, and verification status.")
    
    st.dataframe(filtered_water, use_container_width=True, hide_index=True)
    
    st.warning("⚠️ Satellite & community WASH signals serve as screening indicators. They do not constitute certified microbiological lab analysis.")
    
    if not filtered_water.empty and "reported_date" in filtered_water.columns:
        fig_scatter = px.scatter(
            filtered_water,
            x="reported_date",
            y="reported_concern",
            color="verification_status",
            hover_data=["water_point", "area"],
            title="WASH Concern Timeline & Verification Status",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 4: PRIORITY QUEUE
with tab_queue:
    st.subheader("Priority Operational Review Queue")
    st.write("Filtered queue of facilities requiring human intervention and field validation.")
    
    queue = filtered_sites[filtered_sites["risk_score"] >= 45].sort_values("risk_score", ascending=False).copy()
    
    if not queue.empty:
        st.dataframe(
            queue[["site_name", "area", "service_type", "risk_level", "risk_score", "action"]],
            use_container_width=True,
            hide_index=True
        )
        
        csv_data = queue.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Priority Queue CSV",
            data=csv_data,
            file_name="sizasense_priority_review_queue.csv",
            mime="text/csv"
        )
    else:
        st.success("No facilities currently exceed the priority review threshold in this view.")

# TAB 5: GOVERNANCE & COMPLIANCE
with tab_governance:
    st.subheader("Legal Framework, IP & Data Governance")
    
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("### 📜 License & Trademarks")
        st.markdown("""
        * **Software License:** MIT License (Open Source DPG compliant).
        * **Corporate Legal Owner:** Summernet Group (Pty) Ltd (South Africa), trading as Geo Regreen.
        * **Trademark Protection:** The names *SizaSense*, *Geo Regreen*, and *Summernet Group* are protected corporate trademarks under `NOTICE.md` and are not granted under open-source terms.
        * **Firewalling:** Developed independently from commercial enterprise and mining B2B operations. Zero client data or proprietary mining IP is included.
        """)
        
    with g_col2:
        st.markdown("### 🛡️ Community Safeguarding")
        st.markdown("""
        * **No PII Collection:** Patient names, health diagnoses, and individual location traces are strictly excluded.
        * **Aggregated Signals:** Data indicators represent facility and community-area levels.
        * **Human-in-the-Loop:** Risk scores act as prioritization aids, never automated medical or operational decisions.
        """)