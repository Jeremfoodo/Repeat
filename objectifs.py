import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import gdown

# URLs de Google Drive pour chaque fichier
gdrive_files = {
    'FR': 'https://drive.google.com/uc?id=1HSagRx3aiT3Jb9idOYtdINlYfp4SsqUE',
    'US': 'https://drive.google.com/uc?id=1Ls5d_1G9E3XeiktLzZs6MXTxGzRv7jTb',
    'BE': 'https://drive.google.com/uc?id=1pLdrmiP715kfG_7ToVhXKXqp5lo8-X48',
    'GB': 'https://drive.google.com/uc?id=1j_GSC0NtbI1ozRBA1w1Vp9cpfp974syN',
    'prepared_data': 'https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM'
}

# Télécharger les fichiers depuis Google Drive
def download_files():
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    for key, url in gdrive_files.items():
        output = os.path.join(data_dir, f"{key}.csv")
        gdown.download(url, output, quiet=False)

# Charger les données historiques
def load_historical_data():
    historical_files = {
        'FR': 'data/FR.csv',
        'US': 'data/US.csv',
        'BE': 'data/BE.csv',
        'GB': 'data/GB.csv'
    }

    historical_data = {country: pd.read_csv(file) for country, file in historical_files.items()}
    return historical_data

def prepare_data(historical_data):
    data = []
    for country, df in historical_data.items():
        for segment in ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']:
            row = {
                'Pays': country,
                'Segment': segment,
                'Possible': df[df['Segment'] == segment]['Nombre de Clients Possible'].values[0],
                'Mois Dernier': df[df['Segment'] == segment]['Nombre de Clients Actifs (Mois Précédent)'].values[0],
                'Taux 2023': df[df['Segment'] == segment]['Rapport (%)'].values[0],
                'Taux 2024': df[df['Segment'] == segment]['Rapport (%)'].values[0],  # Modifiable par le manager
                'Repeat Juillet': 0  # Calculé
            }
            data.append(row)
    return pd.DataFrame(data)

def calculate_repeat(df):
    df['Repeat Juillet'] = (df['Mois Dernier'] * (df['Taux 2024'] / 100)).astype(int)
    return df

def objectifs_page():
    st.title('Définir les Objectifs des Account Managers')

    # Télécharger et charger les données historiques
    download_files()
    historical_data = load_historical_data()
    
    df_objectifs = prepare_data(historical_data)
    df_objectifs = calculate_repeat(df_objectifs)

    # Tableau interactif
    gb = GridOptionsBuilder.from_dataframe(df_objectifs)
    gb.configure_columns(["Pays", "Segment", "Possible", "Mois Dernier", "Taux 2023", "Repeat Juillet"], editable=False)
    gb.configure_column("Taux 2024", editable=True, cellStyle=JsCode("""
    function(params) {
        return {
            'backgroundColor': 'yellow'
        }
    }
    """))
    gb.configure_grid_options(domLayout='normal')

    grid_options = gb.build()
    grid_response = AgGrid(df_objectifs, gridOptions=grid_options, enable_enterprise_modules=True, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)
    updated_df = pd.DataFrame(grid_response['data'])

    # Bouton de validation
    if st.button('Valider'):
        password = st.text_input('Entrez le mot de passe pour valider les objectifs:', type='password')
        if password == 'foodostreamlit':
            updated_df = calculate_repeat(updated_df)
            st.success('Les objectifs ont été enregistrés.')
            total_clients_actifs = updated_df['Repeat Juillet'].sum()
            st.info(f'Cela fait un total de {total_clients_actifs} clients actifs.')
            # Sauvegarder les objectifs dans un fichier ou une base de données
            updated_df.to_csv('data/objectifs.csv', index=False)
        else:
            st.error('Mot de passe incorrect.')

    # Charger les objectifs précédemment enregistrés
    try:
        objectifs_precedents = pd.read_csv('data/objectifs.csv')
        st.write('Objectifs précédemment enregistrés:')
        st.write(objectifs_precedents)
    except FileNotFoundError:
        st.write('Aucun objectif précédemment enregistré.')

