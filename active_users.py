import streamlit as st
import pandas as pd
import plotly.express as px

def calculate_active_users(df, target_month):
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    new_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    recent_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    old_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    
    return {
        'Nouveaux Clients': len(new_clients['Restaurant ID'].unique()),
        'Clients Récents': len(recent_clients['Restaurant ID'].unique()),
        'Anciens Clients': len(old_clients['Restaurant ID'].unique())
    }

def active_users_page(historical_data, df):
    st.title("Active Users")

    # Calcul des utilisateurs actifs pour tous les pays confondus
    recent_months = pd.date_range(start='2024-05-01', end='2024-07-01', freq='MS').strftime('%Y-%m').tolist()
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
                 labels={'value':'Nombre de Clients', 'variable':'Segment'})

    fig.add_shape(type="line", x0='2024-05', x1='2024-07', y0=1700, y1=1700,
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
                             labels={'value':'Nombre de Clients', 'variable':'Segment'})
        
        country_fig.update_layout(yaxis=dict(title='Nombre de Clients'), barmode='stack')
        country_fig.update_xaxes(type='category', tickformat='%Y-%m', dtick='M1')
        st.plotly_chart(country_fig)
