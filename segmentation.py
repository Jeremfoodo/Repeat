import streamlit as st
import pandas as pd
import numpy as np
import gdown
from datetime import datetime, timedelta
from plotly import graph_objects as go

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

# Créer le dataframe des clients
@st.cache_data
def create_customer_dataframe(df):
    current_month = datetime.today().replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)

    data = {
        'Restaurant ID': [],
        'Owner email': [],
        'Total_Previous': [],
        'Total_Current': [],
        'Spending Level_Previous': [],
        'Spending Level_Current': [],
        'Segment': []
    }

    df['Commande_Month'] = df['Date de commande'].dt.to_period('M')
    current_month_period = pd.Period(current_month.strftime('%Y-%m'))
    previous_month_period = pd.Period(previous_month.strftime('%Y-%m'))

    for restaurant_id, group in df.groupby('Restaurant ID'):
        account_manager = group.loc[group['Date de commande'].idxmax(), 'Owner email']
        total_current_month = group[group['Commande_Month'] == current_month_period]['Total'].sum()
        total_previous_month = group[group['Commande_Month'] == previous_month_period]['Total'].sum()

        spending_level_current = categorize_customer(total_current_month)
        spending_level_previous = categorize_customer(total_previous_month)

        first_order_date = group['date 1ere commande (Restaurant)'].min().to_period('M')
        if first_order_date == current_month_period:
            segment = 'Acquisition'
        elif first_order_date == previous_month_period:
            segment = 'Nouveau'
        elif first_order_date >= (previous_month - pd.DateOffset(months=4)).to_period('M'):
            segment = 'Récent'
        else:
            segment = 'Ancien'

        data['Restaurant ID'].append(restaurant_id)
        data['Owner email'].append(account_manager)
        data['Total_Previous'].append(total_previous_month)
        data['Total_Current'].append(total_current_month)
        data['Spending Level_Previous'].append(spending_level_previous)
        data['Spending Level_Current'].append(spending_level_current)
        data['Segment'].append(segment)

    return pd.DataFrame(data)

# Charger les données et créer le dataframe des clients
df = load_data()
customer_df = create_customer_dataframe(df)

# Définir la fonction segmentation_page
def segmentation_page(df, customer_df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]
        customer_df = customer_df[customer_df['Restaurant ID'].isin(df['Restaurant ID'])]

    # Calculer les mois dynamiques
    today = datetime.today()
    current_month = today.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    current_month_str = current_month.strftime('%Y-%m')
    previous_month_str = previous_month.strftime('%Y-%m')

    # Générer les heatmaps pour les mois dynamiques
    def generate_heatmap(data, month_str):
        heatmap_data = data[data['Commande_Month'] == month_str].groupby(['Segment', 'Spending Level_Current']).size().unstack(fill_value=0)
        return heatmap_data

    heatmap_data_previous = generate_heatmap(customer_df, previous_month_str)
    heatmap_data_current = generate_heatmap(customer_df, current_month_str)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f'{previous_month.strftime("%B %Y")}')
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_previous.values,
            x=heatmap_data_previous.columns,
            y=heatmap_data_previous.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_previous.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col2:
        st.subheader(f'{current_month.strftime("%B %Y")}')
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_current.values,
            x=heatmap_data_current.columns,
            y=heatmap_data_current.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_current.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Segmentation par account manager
    st.header('Segmentation par Account Manager')
    account_manager = st.selectbox('Sélectionner un account manager', customer_df['Owner email'].unique())
    
    df_account = customer_df[customer_df['Owner email'] == account_manager]

    def render_clients_table(clients, title):
        st.markdown(f"### {title}")
        st.dataframe(clients[['Restaurant ID', 'Owner email', 'Segment', 'Spending Level_Previous', 'Spending Level_Current', 'Total_Previous', 'Total_Current']])

    # Box rouge pour les clients inactifs en juillet
    st.markdown("<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🔴 Clients actifs en {previous_month.strftime('%B %Y')} mais inactifs en {current_month.strftime('%B %Y')}")
    inactive_clients = df_account[df_account['Total_Current'] == 0]
    render_clients_table(inactive_clients, f"Clients inactifs en {current_month.strftime('%B %Y')}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients qui ont baissé dans le tiering
    st.markdown("<div style='background-color: #fd7e14; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟠 Clients actifs en {current_month.strftime('%B %Y')} mais qui ont baissé dans le tiering")
    downgraded_clients = df_account[df_account['Spending Level_Previous'] > df_account['Spending Level_Current']]
    render_clients_table(downgraded_clients, "Clients qui ont baissé dans le tiering")
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé moins en juillet
    st.markdown("<div style='background-color: #ffebcc; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟡 Clients restés dans le même tiering mais dépensé moins en {current_month.strftime('%B %Y')}")
    same_tier_less_spending_clients = df_account[(df_account['Spending Level_Previous'] == df_account['Spending Level_Current']) & (df_account['Total_Previous'] > df_account['Total_Current'])]
    render_clients_table(same_tier_less_spending_clients, "Clients restés dans le même tiering mais dépensé moins en juillet")
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé plus en juillet
    st.markdown("<div style='background-color: #d4edda; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟢 Clients qui ont augmenté leurs dépenses, bravo !")
    increased_spending_clients = df_account[df_account['Total_Current'] > df_account['Total_Previous']]
    render_clients_table(increased_spending_clients, "Clients qui ont augmenté leurs dépenses")
    st.markdown("</div>", unsafe_allow_html=True)

# Appel de la fonction segmentation_page
segmentation_page(df, customer_df)
