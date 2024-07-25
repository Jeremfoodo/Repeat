import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.calculations import get_clients_by_segment_and_spending, get_inactive_clients_july

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

    # Générer les heatmaps pour juin et juillet 2024
    heatmap_data_june, total_clients_june, customer_spending_june = get_clients_by_segment_and_spending(df, '2024-06')
    heatmap_data_july, total_clients_july, customer_spending_july = get_clients_by_segment_and_spending(df, '2024-07')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Juin 2024')
        st.write(f"Nombre total de clients actifs: {total_clients_june}")
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
        st.write(f"Nombre total de clients actifs: {total_clients_july}")
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

    # Segmentation par account manager
    st.header('Segmentation par Account Manager')
    account_manager = st.selectbox('Sélectionner un account manager', df['Owner email'].unique())
    
    df_account = df[df['Owner email'] == account_manager]
    
    heatmap_data_june_account, total_clients_june_account, customer_spending_june_account = get_clients_by_segment_and_spending(df_account, '2024-06')
    heatmap_data_july_account, total_clients_july_account, customer_spending_july_account = get_clients_by_segment_and_spending(df_account, '2024-07')

    col3, col4 = st.columns(2)

    with col3:
        st.subheader(f'Juin 2024 - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_june_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_june_account.values,
            x=heatmap_data_june_account.columns,
            y=heatmap_data_june_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_june_account.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    with col4:
        st.subheader(f'Juillet 2024 - {account_manager}')
        st.write(f"Nombre total de clients actifs: {total_clients_july_account}")
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data_july_account.values,
            x=heatmap_data_july_account.columns,
            y=heatmap_data_july_account.index,
            colorscale='Greens',
            hoverongaps=False,
            showscale=False,
            text=heatmap_data_july_account.values,
            texttemplate="%{text}"
        ))
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Clients actifs en juin mais pas en juillet
    inactive_clients = get_inactive_clients_july(customer_spending_june_account, customer_spending_july_account)
    inactive_clients = inactive_clients.merge(last_order_dates, on='Restaurant ID')
    inactive_clients['Total'] = inactive_clients['Total'].round()

    # Ajouter les colonnes manquantes
    if 'Restaurant' not in inactive_clients.columns:
        inactive_clients = inactive_clients.merge(df[['Restaurant ID', 'Restaurant']], on='Restaurant ID', how='left')
    if 'Segment' not in inactive_clients.columns:
        inactive_clients['Segment'] = 'Unknown'
    if 'Spending Level' not in inactive_clients.columns:
        inactive_clients['Spending Level'] = 'Unknown'

    inactive_clients = inactive_clients.drop_duplicates(subset='Restaurant ID')
    inactive_count = inactive_clients.shape[0]

    # Clients qui ont baissé dans le tiering
    downgraded_clients = customer_spending_june_account[customer_spending_june_account['Restaurant ID'].isin(customer_spending_july_account['Restaurant ID'])]
    downgraded_clients = downgraded_clients.merge(customer_spending_july_account, on='Restaurant ID', suffixes=('_Juin', '_Juillet'))
    downgraded_clients = downgraded_clients[downgraded_clients['Spending Level_Juin'] > downgraded_clients['Spending Level_Juillet']]
    downgraded_clients = downgraded_clients.merge(last_order_dates, on='Restaurant ID')
    downgraded_clients['Total_Juin'] = downgraded_clients['Total_Juin'].round()
    downgraded_clients['Total_Juillet'] = downgraded_clients['Total_Juillet'].round()
    downgraded_clients['Total'] = downgraded_clients['Total_Juillet']

    # Ajouter les colonnes manquantes
    if 'Restaurant' not in downgraded_clients.columns:
        downgraded_clients = downgraded_clients.merge(df[['Restaurant ID', 'Restaurant']], on='Restaurant ID', how='left')
    if 'Segment' not in downgraded_clients.columns:
        downgraded_clients['Segment'] = 'Unknown'
    if 'Spending Level' not in downgraded_clients.columns:
        downgraded_clients['Spending Level'] = 'Unknown'

    downgraded_clients = downgraded_clients.drop_duplicates(subset='Restaurant ID')
    downgraded_count = downgraded_clients.shape[0]

    # Clients restés dans le même tiering mais dépensé moins en juillet
    same_tier_less_spending_clients = customer_spending_june_account[customer_spending_june_account['Restaurant ID'].isin(customer_spending_july_account['Restaurant ID'])]
    same_tier_less_spending_clients = same_tier_less_spending_clients.merge(customer_spending_july_account, on='Restaurant ID', suffixes=('_Juin', '_Juillet'))
    same_tier_less_spending_clients = same_tier_less_spending_clients[(same_tier_less_spending_clients['Spending Level_Juin'] == same_tier_less_spending_clients['Spending Level_Juillet']) & (same_tier_less_spending_clients['Total_Juin'] > same_tier_less_spending_clients['Total_Juillet'])]
    same_tier_less_spending_clients = same_tier_less_spending_clients.merge(last_order_dates, on='Restaurant ID')
    same_tier_less_spending_clients['Total_Juin'] = same_tier_less_spending_clients['Total_Juin'].round()
    same_tier_less_spending_clients['Total_Juillet'] = same_tier_less_spending_clients['Total_Juillet'].round()
    same_tier_less_spending_clients['Total'] = same_tier_less_spending_clients['Total_Juillet']

    # Ajouter les colonnes manquantes
    if 'Restaurant' not in same_tier_less_spending_clients.columns:
        same_tier_less_spending_clients = same_tier_less_spending_clients.merge(df[['Restaurant ID', 'Restaurant']], on='Restaurant ID', how='left')
    if 'Segment' not in same_tier_less_spending_clients.columns:
        same_tier_less_spending_clients['Segment'] = 'Unknown'
    if 'Spending Level' not in same_tier_less_spending_clients.columns:
        same_tier_less_spending_clients['Spending Level'] = 'Unknown'

    same_tier_less_spending_clients = same_tier_less_spending_clients.drop_duplicates(subset='Restaurant ID')
    same_tier_less_spending_count = same_tier_less_spending_clients.shape[0]

    # Clients restés dans le même tiering mais dépensé plus en juillet
    increased_spending_clients = customer_spending_june_account[customer_spending_june_account['Restaurant ID'].isin(customer_spending_july_account['Restaurant ID'])]
    increased_spending_clients = increased_spending_clients.merge(customer_spending_july_account, on='Restaurant ID', suffixes=('_Juin', '_Juillet'))
    increased_spending_clients = increased_spending_clients[(increased_spending_clients['Total_Juin'] < increased_spending_clients['Total_Juillet'])]
    increased_spending_clients = increased_spending_clients.merge(last_order_dates, on='Restaurant ID')
    increased_spending_clients['Total_Juin'] = increased_spending_clients['Total_Juin'].round()
    increased_spending_clients['Total_Juillet'] = increased_spending_clients['Total_Juillet'].round()
    increased_spending_clients['Total'] = increased_spending_clients['Total_Juillet']

    # Ajouter les colonnes manquantes
if 'Restaurant' not in increased_spending_clients.columns:
    increased_spending_clients = increased_spending_clients.merge(df[['Restaurant ID', 'Restaurant']], on='Restaurant ID', how='left')
if 'Segment' not in increased_spending_clients.columns:
    increased_spending_clients['Segment'] = 'Unknown'
if 'Spending Level' not in increased_spending_clients.columns:
    increased_spending_clients['Spending Level'] = 'Unknown'

    increased_spending_clients = increased_spending_clients.drop_duplicates(subset='Restaurant ID')
    increased_spending_count = increased_spending_clients.shape[0]


    # Récapitulatif
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
        <h4>Recap : où sont vos clients en juillet</h4>
        <p><span style='color: #dc3545;'>Rouge</span> : clients qui n'ont pas fait de repeat vs juin</p>
        <p><span style='color: #fd7e14;'>Orange</span> : clients qui ont baissé de catégorie de dépense vs juin</p>
        <p><span style='color: #ffc107;'>Jaune</span> : clients qui ont gardé la catégorie de dépense mais dépensé moins depuis juin</p>
        <p><span style='color: #28a745;'>Vert</span> : clients en augmentation de dépense.</p>
        <div style='display: flex; justify-content: space-around;'>
            <div style='background-color: #f8d7da; padding: 10px; border-radius: 5px; text-align: center;'>
                <strong style='color: #000000;'>{inactive_count}</strong>
                <p>Inactifs en juillet</p>
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
    """.format(
        inactive_count=inactive_count,
        downgraded_count=downgraded_count,
        same_tier_less_spending_count=same_tier_less_spending_count,
        increased_spending_count=increased_spending_count
    ), unsafe_allow_html=True)

    # Afficher les tables de clients
    def render_clients_table(clients, title):
        st.markdown(f"### {title}")
        st.dataframe(clients[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total', 'Dernière commande']])

    # Box rouge pour les clients inactifs en juillet
    st.markdown("<div style='background-color: #f8d7da; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🔴 Clients actifs en juin mais inactifs en juillet ({inactive_count})")
    st.markdown("<small>Ces clients n'ont pas refait d'achat en juillet, essayer un repeat ou comprendre les raisons du churn.</small>", unsafe_allow_html=True)
    render_clients_table(inactive_clients, "Clients inactifs en juillet")
    st.download_button(
        label='Télécharger la liste des clients inactifs en juillet',
        data=inactive_clients.to_csv(index=False),
        file_name='clients_inactifs_juillet.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients qui ont baissé dans le tiering
    st.markdown("<div style='background-color: #fd7e14; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟠 Clients actifs en juillet mais qui ont baissé dans le tiering ({downgraded_count})")
    st.markdown("<small>Ces clients ont baissé de catégorie de dépense, normalement ils peuvent acheter davantage, vérifiez qu'ils ont bien fait leur commande et si non faites un repeat. Si oui, vérifiez qu'ils ont bien acheté suffisamment et proposez un upsell.</small>", unsafe_allow_html=True)
    render_clients_table(downgraded_clients, "Clients qui ont baissé dans le tiering")
    st.download_button(
        label='Télécharger la liste des clients qui ont baissé dans le tiering',
        data=downgraded_clients.to_csv(index=False),
        file_name='clients_baisse_tiering.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé moins en juillet
    st.markdown("<div style='background-color: #ffebcc; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟡 Clients restés dans le même tiering mais dépensé moins en juillet ({same_tier_less_spending_count})")
    st.markdown("<small>Ces clients ont dépensé un peu moins en juillet, même s'ils sont restés dans le même segment. Vous pouvez sans doute voir s'ils peuvent racheter un peu plus.</small>", unsafe_allow_html=True)
    render_clients_table(same_tier_less_spending_clients, "Clients restés dans le même tiering mais dépensé moins en juillet")
    st.download_button(
        label='Télécharger la liste des clients restés dans le même tiering mais dépensé moins en juillet',
        data=same_tier_less_spending_clients.to_csv(index=False),
        file_name='clients_meme_tiering_depense_moins.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Clients restés dans le même tiering mais dépensé plus en juillet
    st.markdown("<div style='background-color: #d4edda; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
    st.subheader(f"🟢 Clients qui ont augmenté leurs dépenses, bravo ! ({increased_spending_count})")
    render_clients_table(increased_spending_clients, "Clients qui ont augmenté leurs dépenses")
    st.download_button(
        label='Télécharger la liste des clients restés dans le même tiering mais dépensé plus en juillet',
        data=increased_spending_clients.to_csv(index=False),
        file_name='clients_meme_tiering_depense_plus.csv',
        mime='text/csv'
    )
    st.markdown("</div>", unsafe_allow_html=True)

