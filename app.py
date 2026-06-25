import streamlit as st
import requests
import pandas as pd
import time

# Code de paiement pour débloquer le téléchargement
PAYMENT_CODE = "LEAD-PRO-2026"

st.set_page_config(page_title="Lead Finder Pro", page_icon="🚀")

st.title("🚀 Lead Finder Pro")
st.write("Générez des listes de prospects gratuitement pour vos clients.")

# Initialisation du session_state pour mémoriser les résultats
if 'leads_df' not in st.session_state:
    st.session_state.leads_df = None

# Sidebar pour les paramètres
with st.sidebar:
    st.header("Paramètres")
    city = st.text_input("Ville", value="Bruxelles")
    business_type = st.text_input("Type d'entreprise (anglais)", value="restaurant")
    st.info("Exemples: hairdresser, cafe, bakery, gym, pharmacy")

if st.button("Lancer la recherche"):
    # Liste de miroirs Overpass
    mirrors = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    
    success = False
    
    for url in mirrors:
        try:
            with st.spinner(f"Recherche en cours (Serveur {url})..."):
                headers = {'User-Agent': 'LeadFinderPro/1.0 (contact: elkhiderkaram190@gmail.com)'}
                
                query = f"""
                [out:json][timeout:25];
                (
                  node["amenity"="{business_type}"](around:10000, 50.85, 4.35);
                  way["amenity"="{business_type}"](around:10000, 50.85, 4.35);
                );
                out center;
                """
                
                response = requests.get(url, params={'data': query}, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    elements = data.get('elements', [])
                    
                    leads = []
                    for el in elements:
                        tags = el.get('tags', {})
                        leads.append({
                            'Nom': tags.get('name', 'N/A'),
                            'Type': business_type,
                            'Adresse': tags.get('addr:street', 'N/A') + " " + tags.get('addr:housenumber', ''),
                            'Ville': city
                        })
                    
                    if leads:
                        st.session_state.leads_df = pd.DataFrame(leads)
                        st.success(f"Trouvé {len(leads)} prospects !")
                    else:
                        st.warning("Aucun prospect trouvé.")
                        st.session_state.leads_df = None
                    
                    success = True
                    break 
                else:
                    time.sleep(1)
                    
        except Exception as e:
            time.sleep(1)

    if not success:
        st.error("Tous les serveurs sont saturés. Veuillez réessayer dans quelques minutes.")

# AFFICHAGE DES RÉSULTATS (si mémorisés dans session_state)
if st.session_state.leads_df is not None:
    df = st.session_state.leads_df
    
    st.divider()
    st.subheader("🔓 Débloquer la liste complète")
    st.write("Pour obtenir la liste complète des prospects en format CSV, merci de régler les frais de service.")
    
    # PayPal
    paypal_email = "elkhiderkaram190@gmail.com"
    amount = "5.00" 
    paypal_url = f"https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business={paypal_email}&amount={amount}&currency_code=EUR&item_name=Liste_Prospects"
    
    st.markdown(f'<a href="{paypal_url}" target="_blank"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_paynow_LG.gif" alt="PayPal Pay Now"></a>', unsafe_allow_html=True)
    
    st.info("Une fois le paiement effectué, vous recevrez un code de confirmation par email.")
    
    user_code = st.text_input("Entrez votre code de confirmation pour télécharger :", type="password")
    
    if user_code == PAYMENT_CODE:
        st.success("✅ Paiement vérifié !")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger la liste complète (CSV)",
            data=csv,
            file_name="prospects_complete.csv",
            mime="text/csv",
        )
    elif user_code:
        st.error("❌ Code incorrect. Veuillez vérifier votre email ou contacter le support.")
    else:
        st.warning("⚠️ Le fichier CSV vous sera envoyé par email ou via Fiverr immédiatement après vérification du paiement.")
