import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# Fonction pour télécharger les données (à partir de Google Drive, cache, etc.)
@st.cache_data
def load_data():
    # Remplacez l'URL ci-dessous par l'URL de votre fichier Google Drive ou utilisez une autre méthode pour charger les données
    url = 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4ægUYZ1AQFsuWja9dM'
    df = pd.read_csv(url, parse_dates=['Date de commande', 'date 1ere commande (Restaurant)'])
    return df


@st.cache_data
def get_clients_by_segment_and_spending(df, year, month):
    # Filtrer les commandes du mois cible
    target_orders = df[(df['Date de commande'].dt.year == year) & (df['Date de commande'].dt.month == month)]
    
    # Calculer le montant total dépensé par chaque client
    customer_spending = target_orders.groupby('Restaurant ID').agg({'Total': 'sum', 'Restaurant': 'first'}).reset_index()
    
    # Définir le niveau de dépense
    def categorize_customer(spent):
        if spent <= 500:
            return 'Basic'
        elif 500 < spent <= 1500:
            return 'Silver'
        elif 1500 < spent <= 2000:
            return 'Gold'
        else:
            return 'High Spender'
    
    customer_spending['Spending Level'] = customer_spending['Total'].apply(categorize_customer)
    
    # Définir les segments
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.year == year].copy()
    acquisition = acquisition[acquisition['date 1ere commande (Restaurant)'].dt.month == month]
    
    previous_month = (pd.to_datetime(f'{year}-{month:02d}-01') - pd.DateOffset(months=1)).month
    previous_year = (pd.to_datetime(f'{year}-{month:02d}-01') - pd.DateOffset(months=1)).year
    
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.year == previous_year].copy()
    nouveaux_clients = nouveaux_clients[nouveaux_clients['date 1ere commande (Restaurant)'].dt.month == previous_month]
    
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(f'{year}-{month:02d}-01') - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )].copy()
    
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(f'{year}-{month:02d}-01') - pd.DateOffset(months=5)).strftime('%Y-%m')].copy()
    
    customer_spending.loc[acquisition['Restaurant ID'].unique(), 'Segment'] = 'Acquisition'
    customer_spending.loc[nouveaux_clients['Restaurant ID'].unique(), 'Segment'] = 'Nouveaux Clients'
    customer_spending.loc[clients_recents['Restaurant ID'].unique(), 'Segment'] = 'Clients Récents'
    customer_spending.loc[anciens_clients['Restaurant ID'].unique(), 'Segment'] = 'Anciens Clients'
    
    # Remplir les segments manquants avec 'Non défini'
    customer_spending['Segment'] = customer_spending['Segment'].fillna('Non défini')
    
    return customer_spending

@st.cache_data
def get_inactive_clients_july(june_data, july_data):
    # Identifier les clients inactifs en juillet
    inactive_clients = june_data[~june_data['Restaurant ID'].isin(july_data['Restaurant ID'])]
    return inactive_clients

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Sélectionner l'account manager
    account_manager = st.selectbox('Sélectionner un account manager', df['Owner email'].unique())
    df_account = df[df['Owner email'] == account_manager]

    # Générer les heatmaps pour juin et juillet 2024
    customer_spending_june = get_clients_by_segment_and_spending(df_account, 2024, 6)
    customer_spending_july = get_clients_by_segment_and_spending(df_account, 2024, 7)

    heatmap_data_june = customer_spending_june.groupby(['Segment', 'Spending Level']).size().unstack(fill_value=0)
    heatmap_data_july = customer_spending_july.groupby(['Segment', 'Spending Level']).size().unstack(fill_value=0)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Juin 2024')
        st.write(f"Nombre total de clients actifs: {len(customer_spending_june)}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_june.values,
            x=heatmap_data_june.columns,
            y=heatmap_data_june.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_june.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col2:
        st.subheader('Juillet 2024')
        st.write(f"Nombre total de clients actifs: {len(customer_spending_july)}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_july.values,
            x=heatmap_data_july.columns,
            y=heatmap_data_july.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_july.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Clients actifs en juin mais pas en juillet
    inactive_clients = get_inactive_clients_july(customer_spending_june, customer_spending_july)
    inactive_count = inactive_clients.shape[0]
    
    st.subheader(f'Clients actifs en juin mais inactifs en juillet ({inactive_count})')
    st.write(inactive_clients[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total']])
    
    # Option de téléchargement pour la liste des clients inactifs en juillet
    st.download_button(
        label='Télécharger la liste des clients inactifs en juillet',
        data=inactive_clients.to_csv(index=False),
        file_name='clients_inactifs_juillet.csv',
        mime='text/csv'
    )

# Charger les données et afficher la page de segmentation
df = load_data()
segmentation_page(df)
