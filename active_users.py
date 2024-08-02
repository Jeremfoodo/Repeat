import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

@st.cache_data
def calculate_active_users(df, target_month):
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    
    return {
        'Nouveaux Clients': len(nouveaux_clients['Restaurant ID'].unique()),
        'Clients Récents': len(clients_recents['Restaurant ID'].unique()),
        'Anciens Clients': len(anciens_clients['Restaurant ID'].unique())
    }

def add_total_labels(fig, df, x_col, y_cols):
    df['Total'] = df[y_cols].sum(axis=1)
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row[x_col],
            y=row['Total'],
            text=f"{row['Total']}",
            showarrow=False,
            font=dict(size=12, color='black'),
            yshift=10
        )

def active_users_page(historical_data, df):
    st.title("Active Users")

    # Calcul des dates dynamiques
    today = datetime.today()
    current_month = today.replace(day=1)
    start_month = (current_month - pd.DateOffset(months=3)).strftime('%Y-%m')
    recent_months = pd.date_range(start=start_month, end=current_month, freq='MS').strftime('%Y-%m').tolist()

    # Calcul des utilisateurs actifs pour tous les pays confondus
    active_users_data = []

    for month in recent_months:
        monthly_data = calculate_active_users(df, month)
        monthly_data['Mois'] = month
        active_users_data.append(monthly_data)

    active_users_df = pd.DataFrame(active_users_data)

    # Vérification des données
    st.write("Données agrégées pour tous les pays confondus")
    st.write(active_users_df)

    # Graphique pour tous les pays confondus
    fig = px.bar(active_users_df, x='Mois', y=['Nouveaux Clients', 'Clients Récents', 'Anciens Clients'], 
                 title='Nombre de Clients Actifs (Tous les pays)',
                 labels={'value':'Nombre de Clients', 'variable':'Segment'},
                 text_auto=True)

    add_total_labels(fig, active_users_df, 'Mois', ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients'])

    fig.add_shape(type="line", x0=start_month, x1=current_month.strftime('%Y-%m'), y0=1700, y1=1700,
                  line=dict(color="Red", width=2, dash="dash"),
                  name="Objectif")
    
    fig.update_layout(yaxis=dict(title='Nombre de Clients'), barmode='stack')
    fig.update_xaxes(type='category', tickformat='%Y-%m', dtick='M1')
    st.plotly_chart(fig)

    # Dropdown pour sélectionner un pays
    country = st.selectbox('Sélectionner un pays', list(historical_data.keys()))

    if country:
        country_df = df[df['Pays'] == country]
        country_active_users_data = []

        for month in recent_months:
            monthly_data = calculate_active_users(country_df, month)
            monthly_data['Mois'] = month
            country_active_users_data.append(monthly_data)

        country_active_users_df = pd.DataFrame(country_active_users_data)

        # Vérification des données par pays
        st.write(f"Données agrégées pour le pays {country}")
        st.write(country_active_users_df)

        # Graphique pour le pays sélectionné
        country_fig = px.bar(country_active_users_df, x='Mois', y=['Nouveaux Clients', 'Clients Récents', 'Anciens Clients'], 
                             title=f'Nombre de Clients Actifs ({country})',
                             labels={'value':'Nombre de Clients', 'variable':'Segment'},
                             text_auto=True)

        add_total_labels(country_fig, country_active_users_df, 'Mois', ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients'])

        country_fig.update_layout(yaxis=dict(title='Nombre de Clients'), barmode='stack')
        country_fig.update_xaxes(type='category', tickformat='%Y-%m', dtick='M1')
        st.plotly_chart(country_fig)
