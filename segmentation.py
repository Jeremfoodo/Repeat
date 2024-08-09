import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.calculations import get_clients_by_segment_and_spending, get_inactive_clients

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

    # Générer les heatmaps pour les mois dynamiques
    heatmap_data_previous, total_clients_previous, customer_spending_previous = get_clients_by_segment_and_spending(df, previous_month_str)
    heatmap_data_current, total_clients_current, customer_spending_current = get_clients_by_segment_and_spending(df, current_month_str)

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
    
    # Réappliquer la fonction pour obtenir les données correctes de segmentation et de niveau de dépense
    heatmap_data_previous_account, total_clients_previous_account, customer_spending_previous_account = get_clients_by_segment_and_spending(df_account, previous_month_str)
    heatmap_data_current_account, total_clients_current_account, customer_spending_current_account = get_clients_by_segment_and_spending(df_account, current_month_str)

    # Utiliser directement customer_spending pour remplir les tableaux
    inactive_clients = get_inactive_clients(customer_spending_previous_account, customer_spending_current_account)
    inactive_clients = inactive_clients.merge(last_order_dates, on='Restaurant ID')
    inactive_clients['Total'] = inactive_clients['Total'].round()

    inactive_count = inactive_clients.shape[0]

    # Clients qui ont baissé dans le tiering
    downgraded_clients = customer_spending_previous_account[
        customer_spending_previous_account['Restaurant ID'].isin(customer_spending_current_account['Restaurant ID'])
    ]
    downgraded_clients = downgraded_clients.merge(customer_spending_current_account, on='Restaurant ID', suffixes=('_Previous', '_Current'))
    downgraded_clients = downgraded_clients[downgraded_clients['Spending Level_Previous'] > downgraded_clients['Spending Level_Current']]
    downgraded_clients = downgraded_clients.merge(last_order_dates, on='Restaurant ID')
    downgraded_clients['Total_Previous'] = downgraded_clients['Total_Previous'].round()
    downgraded_clients['Total_Current'] = downgraded_clients['Total_Current'].round()
    downgraded_clients['Total'] = downgraded_clients['Total_Current']

    downgraded_count = downgraded_clients.shape[0]

    # Clients restés dans le même tiering mais dépensé moins en juillet
    same_tier_less_spending_clients = customer_spending_previous_account[
        customer_spending_previous_account['Restaurant ID'].isin(customer_spending_current_account['Restaurant ID'])
    ]
    same_tier_less_spending_clients = same_tier_less_spending_clients.merge(customer_spending_current_account, on='Restaurant ID', suffixes=('_Previous', '_Current'))
    same_tier_less_spending_clients = same_tier_less_spending_clients[
        (same_tier_less_spending_clients['Spending Level_Previous'] == same_tier_less_spending_clients['Spending Level_Current']) & 
        (same_tier_less_spending_clients['Total_Previous'] > same_tier_less_spending_clients['Total_Current'])
    ]
    same_tier_less_spending_clients = same_tier_less_spending_clients.merge(last_order_dates, on='Restaurant ID')
    same_tier_less_spending_clients['Total_Previous'] = same_tier_less_spending_clients['Total_Previous'].round()
    same_tier_less_spending_clients['Total_Current'] = same_tier_less_spending_clients['Total_Current'].round()
    same_tier_less_spending_clients['Total'] = same_tier_less_spending_clients['Total_Current']

    same_tier_less_spending_count = same_tier_less_spending_clients.shape[0]

    # Clients restés dans le même tiering mais dépensé plus en juillet
    increased_spending_clients = customer_spending_previous_account[
        customer_spending_previous_account['Restaurant ID'].isin(customer_spending_current_account['Restaurant ID'])
    ]
    increased_spending_clients = increased_spending_clients.merge(customer_spending_current_account, on='Restaurant ID', suffixes=('_Previous', '_Current'))
    increased_spending_clients = increased_spending_clients[
        increased_spending_clients['Total_Previous'] < increased_spending_clients['Total_Current']
    ]
    increased_spending_clients = increased_spending_clients.merge(last_order_dates, on='Restaurant ID')
    increased_spending_clients['Total_Previous'] = increased_spending_clients['Total_Previous'].round()
    increased_spending_clients['Total_Current'] = increased_spending_clients['Total_Current'].round()
    increased_spending_clients['Total'] = increased_spending_clients['Total_Current']

    increased_spending_count = increased_spending_clients.shape[0]

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
        st.dataframe(clients[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total', 'Dernière commande']])

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
