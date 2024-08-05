# segmentation_page.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.calculations import get_clients_by_segment_and_spending, get_inactive_clients, get_segment_and_spending_info

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Ajouter la colonne de la dernière commande pour chaque Restaurant ID
    df['Date de commande'] = pd.to_datetime(df['Date de commande'])
    last_order_dates = df.groupby('Restaurant ID')['Date de commande'].max().reset_index()
    last_order_dates.columns = ['Restaurant ID', 'Dernière commande']

    # Calculer les mois dynamiques
    today = datetime.today()
    current_month = today.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    current_month_str = current_month.strftime('%Y-%m')
    previous_month_str = previous_month.strftime('%Y-%m')

    # Obtenir les informations de segmentation et de niveau de dépense pour les mois dynamiques
    customer_info_previous = get_segment_and_spending_info(df, previous_month_str)
    customer_info_current = get_segment_and_spending_info(df, current_month_str)

    heatmap_data_previous, total_clients_previous, _ = get_clients_by_segment_and_spending(df, previous_month_str)
    heatmap_data_current, total_clients_current, _ = get_clients_by_segment_and_spending(df, current_month_str)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f'{previous_month.strftime("%B %Y")}')
        st.write(f"Nombre total de clients actifs: {total_clients_previous}")
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
        st.write(f"Nombre total de clients actifs: {total_clients_current}")
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
    account_manager = st.selectbox('Sélectionner un account manager', df['Owner email'].unique())
    
    df_account = df[df['Owner email'] == account_manager]
    
    customer_info_previous_account = get_segment_and_spending_info(df_account, previous_month_str)
    customer_info_current_account = get_segment_and_spending_info(df_account, current_month_str)

    heatmap_data_previous_account, total_clients_previous_account, _ = get_clients_by_segment_and_spending(df_account, previous_month_str)
    heatmap_data_current_account, total_clients_current_account, _ = get_clients_by_segment_and_spending(df_account, current_month_str)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader(f'{previous_month.strftime("%B %Y")} - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_previous_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_previous_account.values,
            x=heatmap_data_previous_account.columns,
            y=heatmap_data_previous_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_previous_account.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col4:
        st.subheader(f'{current_month.strftime("%B %Y")} - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_current_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_current_account.values,
            x=heatmap_data_current_account.columns,
            y=heatmap_data_current_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_current_account.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Clients inactifs
    inactive_clients = get_inactive_clients(customer_info_previous_account, customer_info_current_account)
    inactive_clients = inactive_clients.merge(last_order_dates, on='Restaurant ID')
    inactive_clients['Total'] = inactive_clients['Total'].round()

    # Clients qui ont baissé dans le tiering
    downgraded_clients = customer_info_previous_account.merge(
        customer_info_current_account,
        on='Restaurant ID',
        suffixes=('_Previous', '_Current')
    )
    downgraded_clients = downgraded_clients[downgraded_clients['Spending Level_Previous'] > downgraded_clients['Spending Level_Current']]
    downgraded_clients = downgraded_clients.merge(last_order_dates, on='Restaurant ID')
    downgraded_clients['Total_Previous'] = downgraded_clients['Total_Previous'].round()
    downgraded_clients['Total_Current'] = downgraded_clients['Total_Current'].round()

    # Clients restés dans le même tiering mais dépensé moins
    same_tier_less_spending_clients = customer_info_previous_account.merge(
        customer_info_current_account,
        on='Restaurant ID',
        suffixes=('_Previous', '_Current')
    )
    same_tier_less_spending_clients = same_tier_less_spending_clients[
        (same_tier_less_spending_clients['Spending Level_Previous'] == same_tier_less_spending_clients['Spending Level_Current']) &
        (same_tier_less_spending_clients['Total_Previous'] > same_tier_less_spending_clients['Total_Current'])
    ]
    same_tier_less_spending_clients = same_tier_less_spending_clients.merge(last_order_dates, on='Restaurant ID')
    same_tier_less_spending_clients['Total_Previous'] = same_tier_less_spending_clients['Total_Previous'].round()
    same_tier_less_spending_clients['Total_Current'] = same_tier_less_spending_clients['Total_Current'].round()

    # Clients restés dans le même tiering mais dépensé plus
    increased_spending_clients = customer_info_previous_account.merge(
        customer_info_current_account,
        on='Restaurant ID',
        suffixes=('_Previous', '_Current')
    )
    increased_spending_clients = increased_spending_clients[increased_spending_clients['Total_Previous'] < increased_spending_clients['Total_Current']]
    increased_spending_clients = increased_spending_clients.merge(last_order_dates, on='Restaurant ID')
    increased_spending_clients['Total_Previous'] = increased_spending_clients['Total_Previous'].round()
    increased_spending_clients['Total_Current'] = increased_spending_clients['Total_Current'].round()

    # Récapitulatif
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
        <h4>Recap : où sont vos clients en {current_month.strftime("%B %Y")}</h4>
        <p><span style='color: #dc3545;'>Rouge</span> : clients qui n'ont pas fait de repeat vs {previous_month.strftime("%B %Y")}</p>
        <p><span style='color: #fd7e14;'>Orange</span> : clients qui ont baissé de catégorie de dépense vs {previous_month.strftime("%B %Y")}</p>
        <p><span style='color: #ffc107;'>Jaune</span> : clients qui ont gardé la catégorie de dépense mais dépensé moins depuis {previous_month.strftime("%B %Y")}</p>
        <p><span style='color: #28a745;'>Vert</span> : clients en augmentation de dépense.</p>
        <div style='display: flex; justify-content: space-around;'>
            <div style='background-color: #f8d7da; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{len(inactive_clients)}</strong>
                <p>Inactifs en {current_month.strftime("%B %Y")}</p>
            </div>
            <div style='background-color: #fd7e14; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{len(downgraded_clients)}</strong>
                <p>Baissé de catégorie</p>
            </div>
            <div style='background-color: #ffebcc; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{len(same_tier_less_spending_clients)}</strong>
                <p>Dépensé moins</p>
            </div>
            <div style='background-color: #d4edda; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{len(increased_spending_clients)}</strong>
                <p>Augmentation de dépense</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Afficher les tables de clients
    def render_clients_table(clients, title):
        st.markdown(f"### {title}")
        st.dataframe(clients[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level_Previous', 'Spending Level_Current', 'Total_Previous', 'Total_Current', 'Dernière commande']])

    # Clients inactifs en juillet
    st.markdown("<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🔴 Clients actifs en {previous_month.strftime('%B %Y')} mais inactifs en {current_month.strftime('%B %Y')}")
    render_clients_table(inactive_clients, f"Clients inactifs en {current_month.strftime('%B %Y')}")

    # Clients qui ont baissé dans le tiering
    st.markdown("<div style='background-color: #fd7e14; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟠 Clients actifs en {current_month.strftime('%B %Y')} mais qui ont baissé dans le tiering")
    render_clients_table(downgraded_clients, "Clients qui ont baissé dans le tiering")

    # Clients restés dans le même tiering mais dépensé moins en juillet
    st.markdown("<div style='background-color: #ffebcc; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟡 Clients restés dans le même tiering mais dépensé moins en {current_month.strftime('%B %Y')}")
    render_clients_table(same_tier_less_spending_clients, "Clients restés dans le même tiering mais dépensé moins en juillet")

    # Clients restés dans le même tiering mais dépensé plus en juillet
    st.markdown("<div style='background-color: #d4edda; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟢 Clients qui ont augmenté leurs dépenses, bravo !")
    render_clients_table(increased_spending_clients, "Clients qui ont augmenté leurs dépenses")
