import streamlit as st
import requests
import os
from PIL import Image
import io

# ── Config page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Harry Potter Recognizer",
    page_icon="🧙",
    layout="wide"
)

# ── Style CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Header personnalisé */
    .hp-header {
        background: #2d1b69;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    .hp-header h1 {
        color: #f0e6d3;
        font-size: 1.4rem;
        margin: 0;
        font-weight: 500;
    }

    /* Zone upload */
    .upload-zone {
        border: 2px dashed #888;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f9f9f9;
        margin-bottom: 1rem;
    }

    /* Carte résultat */
    .result-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
    }

    /* Badge maison */
    .badge-gryffindor  { background: #f9e5e5; color: #c9282d; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; }
    .badge-slytherin   { background: #e5f0e9; color: #1a5c2a; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; }
    .badge-ravenclaw   { background: #e5eaf5; color: #1a2f7a; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; }
    .badge-hufflepuff  { background: #fdf5e0; color: #8a6000; padding: 4px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; }

    /* Masquer le menu Streamlit */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    /* Metric card */
    .metric-box {
        background: #f4f4f4;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #888; margin: 0; }
    .metric-value { font-size: 22px; font-weight: 500; margin: 4px 0 0; }

    /* Info row */
    .info-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        padding: 7px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .info-label { color: #888; }
    .info-value { color: #222; font-weight: 500; }

    /* Success banner */
    .success-banner {
        background: #eef6ee;
        border: 1px solid #a5d6a7;
        border-radius: 8px;
        padding: 10px 14px;
        color: #1b5e20;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* Error banner */
    .error-banner {
        background: #fdecea;
        border: 1px solid #ef9a9a;
        border-radius: 8px;
        padding: 10px 14px;
        color: #b71c1c;
        font-size: 13px;
        margin-bottom: 1rem;
    }

    /* Status footer */
    .footer-bar {
        background: #f4f4f4;
        border-radius: 8px;
        padding: 8px 16px;
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #888;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Config API ────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://api:8000")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hp-header">
    <span style="font-size:24px;">🧙</span>
    <h1>Harry Potter — Character Recognizer</h1>
</div>
""", unsafe_allow_html=True)

# ── Vérification connexion API ────────────────────────────────────────────────
def check_api():
    try:
        r = requests.get(f"{API_URL}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

api_ok = check_api()

# ── Layout deux colonnes ───────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

# ════════════════════════════════════════════════════════════
# COLONNE GAUCHE — Upload
# ════════════════════════════════════════════════════════════
with col_left:
    st.markdown("##### Upload une image")

    uploaded_file = st.file_uploader(
        "Glisse une image ici",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image chargée", use_container_width=True)
    else:
        st.info("Aucune image sélectionnée — glisse un fichier JPG ou PNG.")

    st.markdown("<br>", unsafe_allow_html=True)

    identify_btn = st.button(
        "🔍  Identifier le personnage",
        use_container_width=True,
        disabled=(uploaded_file is None or not api_ok)
    )

# ════════════════════════════════════════════════════════════
# COLONNE DROITE — Résultat
# ════════════════════════════════════════════════════════════
with col_right:
    st.markdown("##### Résultat")

    # État initial — aucune image
    if not uploaded_file:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #aaa;">
            <div style="font-size:40px; margin-bottom:12px;">🔮</div>
            <p style="font-size:14px;">Upload une image pour commencer</p>
        </div>
        """, unsafe_allow_html=True)

    # Image uploadée — en attente du bouton
    elif uploaded_file and not identify_btn:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 1rem; color: #aaa;">
            <div style="font-size:40px; margin-bottom:12px;">✨</div>
            <p style="font-size:14px;">Image prête — clique sur "Identifier" !</p>
        </div>
        """, unsafe_allow_html=True)

    # Bouton cliqué — appel API
    if identify_btn and uploaded_file:
        with st.spinner("Analyse en cours..."):
            try:
                uploaded_file.seek(0)
                response = requests.post(
                    f"{API_URL}/recognize",
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                    timeout=15
                )
                response.raise_for_status()
                result = response.json()

                # ── Succès ────────────────────────────────────────────────
                character = result.get("character", "Inconnu")
                confidence = result.get("confidence", 0)
                info = result.get("info", {})
                house = info.get("house", "Inconnue")
                actor = info.get("actor", "Inconnu")
                wand = info.get("wand", "Inconnue")
                patronus = info.get("patronus", "Inconnu")
                description = info.get("description", "")

                # Badge maison
                house_lower = house.lower()
                badge_class = f"badge-{house_lower}" if house_lower in ["gryffindor","slytherin","ravenclaw","hufflepuff"] else "badge-gryffindor"

                # Banner succès
                st.markdown(f"""
                <div class="success-banner">
                    ✅ Personnage identifié : <strong>{character}</strong>
                </div>
                """, unsafe_allow_html=True)

                # Métriques
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"""
                    <div class="metric-box">
                        <p class="metric-label">Confiance</p>
                        <p class="metric-value">{round(confidence * 100)}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="metric-box">
                        <p class="metric-label">Maison</p>
                        <p class="metric-value"><span class="{badge_class}">{house}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Fiche détaillée
                st.markdown(f"""
                <div class="result-card">
                    <p style="font-size:13px; font-weight:500; margin:0 0 10px;">Informations</p>
                    <div class="info-row">
                        <span class="info-label">🎭 Acteur</span>
                        <span class="info-value">{actor}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">🪄 Baguette</span>
                        <span class="info-value">{wand}</span>
                    </div>
                    <div class="info-row" style="border:none;">
                        <span class="info-label">🦌 Patronus</span>
                        <span class="info-value">{patronus}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Description
                if description:
                    st.markdown(f"""
                    <div style="background:#f9f9f9; border-radius:8px; padding:10px 12px;">
                        <p style="font-size:12px; color:#555; margin:0; line-height:1.6;">{description}</p>
                    </div>
                    """, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown("""
                <div class="error-banner">
                    ❌ Impossible de contacter l'API. Vérifie que le service est bien lancé.
                </div>
                """, unsafe_allow_html=True)

            except requests.exceptions.Timeout:
                st.markdown("""
                <div class="error-banner">
                    ⏱️ L'API met trop de temps à répondre. Réessaie dans quelques secondes.
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f"""
                <div class="error-banner">
                    ❌ Erreur : {str(e)}
                </div>
                """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
status_color = "🟢" if api_ok else "🔴"
status_text  = "API connectée" if api_ok else "API non joignable"

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div class="footer-bar">
    <span>Harry Potter Recognizer — 4IABD</span>
    <span>{status_color} {status_text} — {API_URL}</span>
</div>
""", unsafe_allow_html=True)