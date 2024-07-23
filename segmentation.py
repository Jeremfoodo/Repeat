import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    df = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]
    df['Spending Level'] = pd.cut(df.groupby('Restaurant ID')['Total'].transform('sum'),
                                  bins=[-float('inf'), 500, 1500, 2000, float('inf')],
                                  labels=['Basic', 'Silver', 'Gold', 'High Spenders'])
    df = df.drop_duplicates('Restaurant ID')
    return df.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'count', 'Total': 'sum'}).reset_index()

@st.cache_data
def generate_recommendations(df_june, df_july):
    df_june = df_june[['Restaurant ID', 'Segment', 'Spending Level']].rename(
        columns={'Segment': 'Segment Juin', 'Spending Level': 'Dépense Juin'}
    )
    df_july = df_july[['Restaurant ID', 'Segment', 'Spending Level']].rename(
        columns={'Segment': 'Segment Juillet', 'Spending Level': 'Dépense Juillet'}
    )
    
    merged_df = pd.merge(df_june, df_july, on='Restaurant ID', how='left')

    def get_recommendation(row):
        if pd.isna(row['Segment Juillet']):
            return 'À réactiver ou comprendre la raison du churn'
        elif row['Dépense Juin'] != row['Dépense Juillet']:
            if row['Dépense Juillet'] == 'High Spenders':
                return 'Super ! Continuez comme ça'
            elif row['Dépense Juin'] < row['Dépense Juillet']:
                return 'Super ! Continuez comme ça'
            elif row['Dépense Juin'] > row['Dépense Juillet']:
                return 'À upseller pour plus grosse dépense'
        else:
            return 'Cross-seller ou comprendre pourquoi il ne peut pas acheter plus'

    merged_df['Recommandation'] = merged_df.apply(get_recommendation, axis=1)

    return merged_df[['Restaurant ID', 'Segment Juin', 'Dépense Juin', 'Segment Juillet', 'Dépense Juillet', 'Recommandation']]

def segmentation_page(df):
    st.title('Segmentation des Clients')

    countries = ['FR', 'US', 'GB', 'BE']
    selected_country = st.selectbox('Sélectionner un pays', ['Tous'] + countries)

    if selected_country != 'Tous':
        df = df[df['Pays'] == selected_country]

    heatmap_data_june, total_clients_june = get_clients_by_segment_and_spending(df, '2024-06')
    heatmap_data_july, total_clients_july = get_clients_by_segment_and_spending(df, '2024-07')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f'Juin 2024 - Total Clients: {total_clients_june}')
        fig_june = px.imshow(heatmap_data_june.pivot('Segment', 'Spending Level', 'Restaurant ID'),
                             labels={'color': 'Nombre de Clients'},
                             title='Heatmap Juin 2024')
        st.plotly_chart(fig_june)

    with col2:
        st.subheader(f'Juillet 2024 - Total Clients: {total_clients_july}')
        fig_july = px.imshow(heatmap_data_july.pivot('Segment', 'Spending Level', 'Restaurant ID'),
                             labels={'color': 'Nombre de Clients'},
                             title='Heatmap Juillet 2024')
        st.plotly_chart(fig_july)

    st.subheader('Segmentation par Account Manager')
    account_manager = st.selectbox('Sélectionner un Account Manager', df['Owner email'].unique())

    if account_manager:
        df_account = df[df['Owner email'] == account_manager]
        target_orders_june_account = df_account[df_account['Date de commande'].dt.strftime('%Y-%m') == '2024-06']
        target_orders_july_account = df_account[df_account['Date de commande'].dt.strftime('%Y-%m') == '2024-07']

        heatmap_data_june_account, total_clients_june_account = get_clients_by_segment_and_spending(target_orders_june_account, '2024-06')
        heatmap_data_july_account, total_clients_july_account = get_clients_by_segment_and_spending(target_orders_july_account, '2024-07')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f'Juin 2024 - Total Clients: {total_clients_june_account}')
            fig_june_account = px.imshow(heatmap_data_june_account.pivot('Segment', 'Spending Level', 'Restaurant ID'),
                                         labels={'color': 'Nombre de Clients'},
                                         title='Heatmap Juin 2024')
            st.plotly_chart(fig_june_account)

        with col2:
            st.subheader(f'Juillet 2024 - Total Clients: {total_clients_july_account}')
            fig_july_account = px.imshow(heatmap_data_july_account.pivot('Segment', 'Spending Level', 'Restaurant ID'),
                                         labels={'color': 'Nombre de Clients'},
                                         title='Heatmap Juillet 2024')
            st.plotly_chart(fig_july_account)

        # Générer les recommandations
        df_june_account = target_orders_june_account.drop_duplicates('Restaurant ID')
        df_july_account = target_orders_july_account.drop_duplicates('Restaurant ID')

        recommendations = generate_recommendations(df_june_account, df_july_account)
        st.write(recommendations)

        # Bouton de téléchargement
        csv = recommendations.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les recommandations en CSV",
            data=csv,
            file_name=f'{account_manager}_recommandations.csv',
            mime='text/csv',
        )
