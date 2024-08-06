import streamlit as st
import pandas as pd
import numpy as np
import gdown
from datetime import datetime, timedelta

# Téléchargement et chargement des données
@st.cache_data
def load_data():
    prepared_data_url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
    gdown.download(prepared_data_url, 'prepared_data.csv', quiet=False)
    df = pd.read_csv('prepared_data.csv')
    df['Date de commande'] = pd.to_datetime(df['Date de commande'])
    df['date 1ere commande (Restaurant)'] = pd.to_datetime(df['date 1ere commande (Restaurant)'])
    return df

# Fonction de catégorisation des clients par niveau de dépense
def categorize_customer(spent):
    if spent <= 500:
        return 'Basic'
    elif 500 < spent <= 1500:
        return 'Silver'
    elif 1500 < spent <= 2000:
        return 'Gold'
    else:
        return 'High Spenders'

# Fonction pour obtenir la catégorie des clients
def get_customer_category(first_order_date, current_month):
    if first_order_date >= current_month:
        return 'Acquisition'
    elif first_order_date >= current_month - pd.DateOffset(months=1):
        return 'Nouveau'
    elif first_order_date >= current_month - pd.DateOffset(months=5):
        return 'Récent'
    else:
        return 'Ancien'

# Fonction principale pour créer le dataframe des clients avec les informations nécessaires
@st.cache_data
def create_customer_dataframe(df):
    # Calcul des dates de mois en cours et précédent
    today = datetime.today()
    current_month = today.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # Initialisation des colonnes de résultat
    result = []

    for restaurant_id, group in df.groupby('Restaurant ID'):
        account_manager = group.loc[group['Date de commande'].idxmax()]['Owner email']
        total_current_month = group[group['Date de commande'].dt.to_period('M') == current_month.to_period('M')]['Total'].sum()
        total_previous_month = group[group['Date de commande'].dt.to_period('M') == previous_month.to_period('M')]['Total'].sum()
        
        spending_level_current = categorize_customer(total_current_month)
        spending_level_previous = categorize_customer(total_previous_month)
        
        first_order_date = group['date 1ere commande (Restaurant)'].min()
        customer_category = get_customer_category(first_order_date, current_month)
        
        result.append({
            'Restaurant ID': restaurant_id,
            'Owner email': account_manager,
            'Total Current Month': total_current_month,
            'Total Previous Month': total_previous_month,
            'Spending Level Current': spending_level_current,
            'Spending Level Previous': spending_level_previous,
            'Customer Category': customer_category
        })
    
    result_df = pd.DataFrame(result)
    return result_df

# Charger les données et créer le dataframe des clients
df = load_data()
customer_df = create_customer_dataframe(df)

def segmentation_page(df, customer_df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Sélectionner l'account manager
    account_manager = st.selectbox('Sélectionner un account manager', customer_df['Owner email'].unique())
    df_account = customer_df[customer_df['Owner email'] == account_manager]

    # Clients inactifs
    inactive_clients = df_account[(df_account['Total Previous Month'] > 0) & (df_account['Total Current Month'] == 0)]

    # Clients downgraded
    downgraded_clients = df_account[(df_account['Spending Level Previous'] > df_account['Spending Level Current'])]

    # Clients same tier less spending
    same_tier_less_spending_clients = df_account[
        (df_account['Spending Level Previous'] == df_account['Spending Level Current']) & 
        (df_account['Total Previous Month'] > df_account['Total Current Month'])
    ]

    # Clients increased spending
    increased_spending_clients = df_account[df_account['Total Current Month'] > df_account['Total Previous Month']]

    # Récapitulatif
    inactive_count = inactive_clients.shape[0]
    downgraded_count = downgraded_clients.shape[0]
    same_tier_less_spending_count = same_tier_less_spending_clients.shape[0]
    increased_spending_count = increased_spending_clients.shape[0]

    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
        <h4>Recap : où sont vos clients en {current_month.strftime("%B %Y")}</h4>
        <p><span style='color: #dc3545;'>Rouge</span> : clients qui n'ont pas fait de repeat vs {previous_month.strftime("%B %Y")}</p>
        <p><span style='color: #fd7e14;'>Orange</span> : clients qui ont baissé de catégorie de dépense vs {previous_month.strftime("%B %Y")}</p>
        <p><span style='color: #ffc107;'>Jaune</span> : clients qui ont gardé la catégorie de dépense mais dépensé moins depuis {previous_month.strftime("%B %Y")}</p>
        <p><span style='color: #28a745;'>Vert</span> : clients en augmentation de dépense.</p>
        <div style='display: flex; justify-content: space-around;'>
            <div style='background-color: #f8d7da; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{inactive_count}</strong>
                <p>Inactifs en {current_month.strftime("%B %Y")}</p>
            </div>
            <div style='background-color: #fd7e14; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{downgraded_count}</strong>
                <p>Baissé de catégorie</p>
            </div>
            <div style='background-color: #ffebcc; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{same_tier_less_spending_count}</strong>
                <p>Dépensé moins</p>
            </div>
            <div style='background-color: #d4edda; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{increased_spending_count}</strong>
                <p>Augmentation de dépense</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Afficher les tables de clients
    def render_clients_table(clients, title):
        st.markdown(f"### {title}")
        st.dataframe(clients[['Restaurant ID', 'Owner email', 'Spending Level Previous', 'Spending Level Current', 'Total Previous Month', 'Total Current Month', 'Customer Category']])

    # Box rouge pour les clients inactifs en juillet
    st.markdown("<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🔴 Clients actifs en {previous_month.strftime('%B %Y')} mais inactifs en {current_month.strftime('%B %Y')} ({inactive_count})")
    st.markdown("<small>Ces clients n'ont pas refait d'achat en juillet, essayer un repeat ou comprendre les raisons du churn.</small>", unsafe_allow_html=True)
    render_clients_table(inactive_clients, f"Clients inactifs en {current_month.strftime('%B %Y')}")
    st.download_button(
        label=f'Télécharger la liste des clients inactifs en {current_month.strftime("%B %Y")}',
        data=inactive_clients.to_csv(index=False),
        file_name=f'clients_inactifs_{current_month.strftime("%B_%Y")}.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients qui ont baissé dans le tiering
    st.markdown("<div style='background-color: #fd7e14; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟠 Clients actifs en {current_month.strftime('%B %Y')} mais qui ont baissé dans le tiering ({downgraded_count})")
    st.markdown("<small>Ces clients ont baissé de catégorie de dépense, normalement ils peuvent acheter davantage, vérifiez qu'ils ont bien fait leur commande et si non faites un repeat. Si oui, vérifiez qu'ils ont bien acheté suffisamment et proposez un upsell.</small>", unsafe_allow_html=True)
    render_clients_table(downgraded_clients, "Clients qui ont baissé dans le tiering")
    st.download_button(
        label=f'Télécharger la liste des clients qui ont baissé dans le tiering',
        data=downgraded_clients.to_csv(index=False),
        file_name=f'clients_baisse_tiering_{current_month.strftime("%B_%Y")}.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé moins en juillet
    st.markdown("<div style='background-color: #ffebcc; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟡 Clients restés dans le même tiering mais dépensé moins en {current_month.strftime('%B %Y')} ({same_tier_less_spending_count})")
    st.markdown("<small>Ces clients ont dépensé un peu moins en juillet, même s'ils sont restés dans le même segment. Vous pouvez sans doute voir s'ils peuvent racheter un peu plus.</small>", unsafe_allow_html=True)
    render_clients_table(same_tier_less_spending_clients, "Clients restés dans le même tiering mais dépensé moins en juillet")
    st.download_button(
        label=f'Télécharger la liste des clients restés dans le même tiering mais dépensé moins en {current_month.strftime("%B %Y")}',
        data=same_tier_less_spending_clients.to_csv(index=False),
        file_name=f'clients_meme_tiering_depense_moins_{current_month.strftime("%B_%Y")}.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé plus en juillet
    st.markdown("<div style='background-color: #d4edda; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟢 Clients qui ont augmenté leurs dépenses, bravo ! ({increased_spending_count})")
    render_clients_table(increased_spending_clients, "Clients qui ont augmenté leurs dépenses")
    st.download_button(
        label=f'Télécharger la liste des clients restés dans le même tiering mais dépensé plus en {current_month.strftime("%B %Y")}',
        data=increased_spending_clients.to_csv(index=False),
        file_name=f'clients_meme_tiering_depense_plus_{current_month.strftime("%B_%Y")}.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    # Charger les données et afficher la page de segmentation
    segmentation_page(df, customer_df)
