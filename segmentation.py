import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def segment_customers(data, year, month):
    # Convert 'Date de commande' to datetime
    data['Date de commande'] = pd.to_datetime(data['Date de commande'], format='%Y-%m-%d %H:%M:%S')
    
    # Filter data for the specified month and year
    filtered_data = data[(data['Date de commande'].dt.year == year) & 
                         (data['Date de commande'].dt.month == month)]
    
    # Calculate total amount spent by each client in the specified month
    customer_spending = filtered_data.groupby('Restaurant ID').agg({
        'Total': 'sum',
        'Restaurant': 'first'  # Get the restaurant name
    }).reset_index()
    
    # Define the segmentation criteria
    def categorize_customer(spent):
        if spent <= 500:
            return 'Basic'
        elif 500 < spent <= 1500:
            return 'Silver'
        elif 1500 < spent <= 2000:
            return 'Gold'
        else:
            return 'High Spenders'
    
    # Apply categorization
    customer_spending['Spending Level'] = customer_spending['Total'].apply(categorize_customer)
    
    return customer_spending

@st.cache_data
def get_clients_by_segment_and_spending(df, target_month):
    year, month = map(int, target_month.split('-'))
    customer_spending = segment_customers(df, year, month)
    
    # Define the segments
    acquisition = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')]
    clients_recents = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = df[df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]
    
    customer_spending.loc[customer_spending['Restaurant ID'].isin(acquisition['Restaurant ID']), 'Segment'] = 'Acquisition'
    customer_spending.loc[customer_spending['Restaurant ID'].isin(nouveaux_clients['Restaurant ID']), 'Segment'] = 'Nouveaux Clients'
    customer_spending.loc[customer_spending['Restaurant ID'].isin(clients_recents['Restaurant ID']), 'Segment'] = 'Clients Récents'
    customer_spending.loc[customer_spending['Restaurant ID'].isin(anciens_clients['Restaurant ID']), 'Segment'] = 'Anciens Clients'
    
    # Compter les clients par segment et niveau de dépense
    heatmap_data = customer_spending.groupby(['Segment', 'Spending Level']).agg({'Restaurant ID': 'nunique'}).reset_index()
    
    # Pivot pour obtenir le format désiré
    heatmap_pivot = heatmap_data.pivot(index='Segment', columns='Spending Level', values='Restaurant ID').fillna(0)
    
    total_clients = customer_spending['Restaurant ID'].nunique()
    
    return heatmap_pivot, total_clients, customer_spending

def segmentation_page(df):
    st.title('Segmentation')

    # Sélectionner le pays
    selected_country = st.selectbox('Sélectionner un pays', ['Tous les pays', 'FR', 'US', 'GB', 'BE'])
    if selected_country != 'Tous les pays':
        df = df[df['Pays'] == selected_country]

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

    # Vérification de la segmentation pour juin 2024
    st.subheader('Vérification de la segmentation pour juin 2024')
    st.write(customer_spending_june[['Restaurant ID', 'Restaurant', 'Total', 'Spending Level']])

# Charger les données et afficher la page de segmentation
df = pd.read_csv('/mnt/data/prepared_data.csv', parse_dates=['Date de commande', 'date 1ere commande (Restaurant)'])
segmentation_page(df)
