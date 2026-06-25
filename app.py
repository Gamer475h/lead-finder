import streamlit as st
import requests
import pandas as pd

# Code de paiement pour débloquer le téléchargement
PAYMENT_CODE = "LEAD-PRO-2026"

st.set_page_config(page_title="Lead Finder Pro", page_icon="🚀")

st.title("🚀 Lead Finder Pro")
st.write("Générez des listes de prospects gratuitement pour vos clients.")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("Paramètres")
    city = st.text_input("Ville", value="Bruxelles")
    business_type = st.text_input("Type d'entreprise (anglais)", value="restaurant")
    st.info("Exemples: hairdresser, cafe, bakery, gym, pharmacy")

if st.button("Lancer la recherche"):
    with st.spinner("Recherche en cours..."):
        overpass_url = "https://overpass-api.de/api/interpreter"
        headers = {'User-Agent': 'LeadFinderPro/1.0 (contact: elkhiderkaram190@gmail.com)'}
        
        query = f"""
        [out:json];
        (
          node["amenity"="{business_type}"](around:10000, 50.85, 4.35);
          way["amenity"="{business_type}"](around:10000, 50.85, 4.35);
        );
        out center;
        """
        
        try:
            response = requests.get(overpass_url, params={'data': query}, headers=headers)
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
                    df = pd.DataFrame(leads)
                    st.success(f"Trouvé {len(leads)} prospects !")
                    
                    st.divider()
                    st.subheader("🔓 Débloquer la liste complète")
                    st.write("Pour obtenir la liste complète des prospects en format CSV, merci de régler les frais de service.")
                    
                    # PayPal Configuration
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
                else:
                    st.warning("Aucun prospect trouvé. Essayez un autre type d'entreprise.")
            else:
                st.error(f"Erreur serveur {response.status_code}. L'API est peut-être saturée.")
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
