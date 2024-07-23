import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    bins = [0, 500, 1500, 2000, float('inf')]
    labels = ['Basic', 'Silver', 'Gold', 'High Spenders']
    target_orders['Spending Level'] = pd.cut(target_orders.groupby('Restaurant ID')['Total'].transform('sum'), bins=bins, labels=labels)
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
    heatmap_data = target_orders.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique'}).reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Restaurant ID').fillna(0)
    total_clients = target_orders['Restaurant ID'].nunique()
    return heatmap_pivot, total_clients, target_orders

def generate_recommendations(df_june, df_july):
    if 'Segment' not in df_june.columns or 'Spending Level' not in df_june.columns:
        df_june = get_clients_by_segment_and_spending(df_june, '2024-06')[2]
    if 'Segment' not in df_july.columns or 'Spending Level' not in df_july.columns:
        df_july = get_clients_by_segment_and_spending(df_july, '2024-07')[2]
    df_june = df_june.drop_duplicates('Restaurant ID')
    df_june = df_june[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total']].rename(
        columns={'Segment': 'Segment Juin', 'Spending Level': 'Dépense Juin', 'Total': 'Total Juin'}
    )
    df_july = df_july[['Restaurant ID', 'Restaurant', 'Segment', 'Spending Level', 'Total']].rename(
        columns={'Segment': 'Segment Juillet', 'Spending Level': 'Dépense Juillet', 'Total': 'Total Juillet'}
    )
    df_combined = pd.merge(df_june, df_july, on=['Restaurant ID', 'Restaurant'], how='left', indicator=True)
    df_combined['Actif Juillet'] = df_combined['_merge'] == 'both'
    df_combined = df_combined.drop(columns=['_merge'])
    df_combined['Recommandation'] = df_combined.apply(recommend, axis=1)
    return df_combined

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
    elif row['Total Juillet'] < row['Total Juin']:
        return 'Clients qui reste dans le meme Tier, mais qui ont quand meme diminué leurs dépenses'
    else:
        return 'Cross-seller ou comprendre pourquoi il ne peut pas acheter plus'

def segmentation_page(df):
    st.title('Segmentation')
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]
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
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        fig.add_trace(go.Scatter(
            x=['Total']*len(heatmap_data_june.index),
            y=heatmap_data_june.index,
            text=heatmap_data_june.sum(axis=1),
            mode="text",
            textposition="middle right"
        ))
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
        fig.add_trace(go.Scatter(
            x=['Total']*len(heatmap_data_july.index),
            y=heatmap_data_july.index,
            text=heatmap_data_july.sum(axis=1),
            mode="text",
            textposition="middle right"
        ))
        st.plotly_chart(fig)
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
        fig.update_layout(
            title='Nombre de Clients par Segment et Niveau de Dépense',
            xaxis_title='Niveau de Dépense',
            yaxis_title='Segment',
        )
        fig.add_trace(go.Scatter(
            x=['Total']*len(heatmap_data_june_account.index),
            y=heatmap_data_june_account.index,
            text=heatmap_data_june_account.sum(axis=1),
            mode="text",
            textposition="middle right"
        ))
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
        fig.add_trace(go.Scatter(
            x=['Total']*len(heatmap_data_july_account.index),
            y=heatmap_data_july_account.index,
            text=heatmap_data_july_account.sum(axis=1),
            mode="text",
            textposition="middle right"
        ))
        st.plotly_chart(fig)
    df_june_account = target_orders_june_account.drop_duplicates('Restaurant ID')
    df_july_account = target_orders_july_account.drop_duplicates('Restaurant ID')
    recommendations = generate_recommendations(df_june_account, df_july_account)
    def create_box(recommendations, condition, title, strategy, color):
        filtered_recommendations = recommendations[condition]
        st.markdown(f"<div style='background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        st.subheader(f"{title} ({len(filtered_recommendations)})")
        st.markdown(f"<p style='font-size: 12px;'>{strategy}</p>", unsafe_allow_html=True)
        st.write(filtered_recommendations[['Restaurant ID', 'Restaurant', 'Segment Juin', 'Dépense Juin', 'Total Juin', 'Total Juillet']])
        csv = filtered_recommendations.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger en CSV",
            data=csv,
            file_name=f'{title.replace(" ", "_").lower()}_{account_manager}.csv',
            mime='text/csv',
        )
        st.markdown("</div>", unsafe_allow_html=True)
    create_box(
        recommendations,
        recommendations['Recommandation'] == 'A réactiver ou comprendre raison du churn',
        "Clients pas revenus entre juin et juillet",
        "Clients à faire un repeat, ou comprendre raison du churn",
        "#FFCCCC"
    )
    create_box(
        recommendations,
        recommendations['Recommandation'] == 'A upseller pour plus grosse dépense',
        "Clients avec dépense inférieure en juillet",
        "Clients à upseller pour plus grosse dépense",
        "#FFCC99"
    )
    create_box(
        recommendations,
        recommendations['Recommandation'] == 'Clients qui reste dans le meme Tier, mais qui ont quand meme diminué leurs dépenses',
        "Clients qui restent dans le même Tier, mais qui ont quand même diminué leurs dépenses",
        "Clients à cross-seller ou comprendre pourquoi ils ne peuvent pas acheter plus",
        "#FFFF99"
    )
    create_box(
        recommendations,
        recommendations['Recommandation'] == 'Super !',
        "Clients ayant augmenté leurs dépenses",
        "Super !",
        "#CCFFCC"
    )
