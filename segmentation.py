import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    # Filtrer les commandes du mois cible
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    
    # Convertir la colonne 'Total' en numérique
    target_orders['Total'] = pd.to_numeric(target_orders['Total'].str.replace(',', '.'), errors='coerce')
    
    # Définir le niveau de dépense
    bins = [0, 500, 1500, 2000, float('inf')]
    labels = ['Basic', 'Silver', 'Gold', 'High Spenders']
    target_orders['Spending Level'] = pd.cut(target_orders.groupby('Restaurant ID')['Total'].transform('sum'), bins=bins, labels=labels)
    
    # Définir les segments
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')
    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    
    target_orders.loc[acquisition.index, 'Segment'] = 'Acquisition'
    target_orders.loc[nouveaux_clients.index, 'Segment'] = 'Nouveaux Clients'
    target_orders.loc[clients_recents.index, 'Segment'] = 'Clients Récents'
    target_orders.loc[anciens_clients.index, 'Segment'] = 'Anciens Clients'
    
    # Compter les clients par segment et niveau de dépense
    heatmap_data = target_orders.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique'}).reset_index()
    
    # Pivot pour obtenir le format désiré
    heatmap_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Restaurant ID').fillna(0)
    
    total_clients = target_orders['Restaurant ID'].nunique()
    
    return heatmap_pivot, total_clients, target_orders

def generate_recommendations(df_june, df_july):
    if 'Segment' not in df_june.columns or 'Spending Level' not in df_june.columns:
        df_june = get_clients_by_segment_and_spending(df_june, '2024-06')[2]
    if 'Segment' not in df_july.columns or 'Spending Level' not in df_july.columns:
        df_july = get_clients_by_segment_and_spending(df_july, '2024-07')[2]

    # Filtrer uniquement les clients actifs en juin
    df_june = df_june.drop_duplicates('Restaurant ID')
    
    df_june = df_june[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level']].rename(
        columns={'Segment': 'Segment Juin', 'Spending Level': 'Dépense Juin'}
    )
    df_july = df_july[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level']].rename(
        columns={'Segment': 'Segment Juillet', 'Spending Level': 'Dépense Juillet'}
    )
    df_combined = pd.merge(df_june, df_july, on=['Restaurant ID', 'Restaurant'], how='left', indicator=True)
    df_combined['Actif Juillet'] = df_combined['_merge'] == 'both'
    df_combined = df_combined.drop(columns=['_merge'])
    
    def recommend(row):
        if not row['Actif Juillet']:
            return 'A réactiver ou comprendre raison du churn'
        elif row['Dépense Juin'] != row['Dépense Juillet']:
            if row['Dépense Juin'] == 'High Spenders' and row['Dépense Juillet'] != 'High Spenders':
                return 'A upseller pour plus grosse dépense'
            elif row['Dépense Juin'] != 'High Spenders' and row['Dépense Juillet'] == 'High Spenders':
                return 'Super !'
            else:
                return 'A upseller pour plus grosse dépense'
        elif row['Dépense Juin'] == row['Dépense Juillet']:
            if row['Dépense Juin'] != row['Dépense Juillet']:
                return 'Clients qui reste dans le même Tier, mais qui ont quand même diminué leurs dépenses'
            else:
                return 'Cross-seller ou comprendre pourquoi il ne peut pas acheter plus'
        else:
            return 'Super !'
    
    df_combined['Recommandation'] = df_combined.apply(recommend, axis=1)
    return df_combined

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

    # Générer les heatmaps pour juin et juillet 2024
    heatmap_data_june, total_clients_june, target_orders_june = get_clients_by_segment_and_spending(df, '2024-06')
    heatmap_data_july, total_clients_july, target_orders_july = get_clients_by_segment_and_spending(df, '2024-07')

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
        for i, segment in enumerate(heatmap_data_june.index):
            total_segment = heatmap_data_june.loc[segment].sum()
            fig.add_annotation(x='Total', y=segment, text=str(total_segment), showarrow=False, font=dict(color="black"))

        total_all_segments = heatmap_data_june.sum().sum()
        fig.add_annotation(x='Total', y='Total', text=str(total_all_segments), showarrow=False, font=dict(color="black"))

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
        for i, segment in enumerate(heatmap_data_july.index):
            total_segment = heatmap_data_july.loc[segment].sum()
            fig.add_annotation(x='Total', y=segment, text=str(total_segment), showarrow=False, font=dict(color="black"))

        total_all_segments = heatmap_data_july.sum().sum()
        fig.add_annotation(x='Total', y='Total', text=str(total_all_segments), showarrow=False, font=dict(color="black"))

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
    
    heatmap_data_june_account, total_clients_june_account, target_orders_june_account = get_clients_by_segment_and_spending(df_account, '2024-06')
    heatmap_data_july_account, total_clients_july_account, target_orders_july_account = get_clients_by_segment_and_spending(df_account, '2024-07')

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
        for i, segment in enumerate(heatmap_data_june_account.index):
            total_segment = heatmap_data_june_account.loc[segment].sum()
            fig.add_annotation(x='Total', y=segment, text=str(total_segment), showarrow=False, font=dict(color="black"))

        total_all_segments = heatmap_data_june_account.sum().sum()
        fig.add_annotation(x='Total', y='Total', text=str(total_all_segments), showarrow=False, font=dict(color="black"))

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
        for i, segment in enumerate(heatmap_data_july_account.index):
            total_segment = heatmap_data_july_account.loc[segment].sum()
            fig.add_annotation(x='Total', y=segment, text=str(total_segment), showarrow=False, font=dict(color="black"))

        total_all_segments = heatmap_data_july_account.sum().sum()
        fig.add_annotation(x='Total', y='Total', text=str(total_all_segments), showarrow=False, font=dict(color="black"))

        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        st.plotly_chart(fig)

    # Générer les recommandations
    df_june_account = target_orders_june_account.drop_duplicates('Restaurant ID')
    df_july_account = target_orders_july_account.drop_duplicates('Restaurant ID')

    recommendations = generate_recommendations(df_june_account, df_july_account)

    # Filtrer les recommandations
    not_returned_clients = recommendations[recommendations['Recommandation'] == 'A réactiver ou comprendre raison du churn']
    decreased_spending_clients = recommendations[
        (recommendations['Recommandation'] == 'A upseller pour plus grosse dépense') &
        (recommendations['Dépense Juin'] != recommendations['Dépense Juillet'])
    ]
    same_spending_clients = recommendations[
        (recommendations['Recommandation'] == 'Cross-seller ou comprendre pourquoi il ne peut pas acheter plus') &
        (recommendations['Dépense Juin'] == recommendations['Dépense Juillet'])
    ]
    increased_spending_clients = recommendations[recommendations['Recommandation'] == 'Super !']

    # Afficher les tableaux
    st.subheader(f'Clients pas revenus entre juin et juillet ({len(not_returned_clients)})')
    st.markdown('<span style="color:red;">Clients à faire un repeat, ou comprendre raison du churn</span>', unsafe_allow_html=True)
    st.dataframe(not_returned_clients[['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin']].style.applymap(lambda x: 'background-color: red', subset=['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin']))

    st.subheader(f'Clients avec une dépense réduite en juillet ({len(decreased_spending_clients)})')
    st.markdown('<span style="color:orange;">Clients actifs en juin et en juillet, mais dans un niveau de dépense inférieur en juillet</span>', unsafe_allow_html=True)
    st.dataframe(decreased_spending_clients[['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Dépense Juillet']].style.applymap(lambda x: 'background-color: orange', subset=['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Dépense Juillet']))

    st.subheader(f'Clients qui restent dans le même Tier, mais qui ont quand même diminué leurs dépenses ({len(same_spending_clients)})')
    st.markdown('<span style="color:yellow;">Clients actifs en juin et en juillet, dans la même catégorie de dépense, mais avec un total inférieur en juillet</span>', unsafe_allow_html=True)
    st.dataframe(same_spending_clients[['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Dépense Juillet']].style.applymap(lambda x: 'background-color: yellow', subset=['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Dépense Juillet']))

    st.subheader(f'Clients avec une dépense augmentée en juillet ({len(increased_spending_clients)})')
    st.markdown('<span style="color:green;">Clients actifs en juin et en juillet, avec une augmentation de leur dépense en juillet</span>', unsafe_allow_html=True)
    st.dataframe(increased_spending_clients[['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Dépense Juillet']].style.applymap(lambda x: 'background-color: green', subset=['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Dépense Juillet']))

    # Boutons de téléchargement pour chaque catégorie
    def download_button(label, data):
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=label,
            data=csv,
            file_name=f'{account_manager}_{label.replace(" ", "_").lower()}.csv',
            mime='text/csv',
        )

    download_button("Télécharger les clients pas revenus", not_returned_clients)
    download_button("Télécharger les clients avec dépense réduite", decreased_spending_clients)
    download_button("Télécharger les clients dans même Tier avec dépense réduite", same_spending_clients)
    download_button("Télécharger les clients avec dépense augmentée", increased_spending_clients)

