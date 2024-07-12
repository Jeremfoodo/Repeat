import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from sqlalchemy.orm import Session
from db import SessionLocal, Objectif

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Charger les objectifs précédemment enregistrés
def load_objectifs(db: Session):
    objectifs = db.query(Objectif).all()
    if objectifs:
        return pd.DataFrame([o.__dict__ for o in objectifs])
    else:
        return pd.DataFrame()

# Sauvegarder les objectifs dans la base de données
def save_objectifs(db: Session, df: pd.DataFrame):
    db.query(Objectif).delete()
    for _, row in df.iterrows():
        obj = Objectif(
            pays=row['Pays'],
            segment=row['Segment'],
            possible=row['Possible'],
            mois_dernier=row['Mois Dernier'],
            juillet_now=row['Juillet NOW'],
            taux_2023=row['Taux 2023'],
            taux_2024=row['Taux 2024'],
            obj_juillet=row['OBJ Juillet'],
            reste_a_faire=row['Reste à faire']
        )
        db.add(obj)
    db.commit()
    # Vérification des données enregistrées
    for obj in db.query(Objectif).all():
        st.write(obj)

# Charger les données historiques
def load_historical_data():
    historical_files = {
        'FR': 'https://drive.google.com/uc?id=1HSagRx3aiT3Jb9idOYtdINlYfp4SsqUE',
        'US': 'https://drive.google.com/uc?id=1Ls5d_1G9E3XeiktLzZs6MXTxGzRv7jTb',
        'BE': 'https://drive.google.com/uc?id=1pLdrmiP715kfG_7ToVhXKXqp5lo8-X48',
        'GB': 'https://drive.google.com/uc?id=1j_GSC0NtbI1ozRBA1w1Vp9cpfp974syN'
    }

    historical_data = {country: pd.read_csv(file) for country, file in historical_files.items()}
    return historical_data

# Charger les données récentes
def load_recent_data():
    return pd.read_csv('https://drive.google.com/uc?id=1krOrcWcYr2F_shA4gUYZ1AQFsuWja9dM', parse_dates=['date 1ere commande (Restaurant)', 'Date de commande'], decimal='.')

# Nettoyer et traiter les données récentes
def preprocess_data(df):
    to_exclude_commande = ['CANCELLED', 'ABANDONED', 'FAILED', 'WAITING']
    to_exclude_paiement = ['CANCELLED', 'ERROR']
    df = df[~df['Statut commande'].isin(to_exclude_commande)]
    df = df[~df['Statut paiement'].isin(to_exclude_paiement)]
    df = df[~df['Canal'].str.contains('trading', case=False, na=False)]
    df['Mois'] = df['Date de commande'].dt.strftime('%Y-%m')
    return df

def calculate_segments_for_month(df, target_month):
    previous_month = (pd.to_datetime(target_month) - pd.DateOffset(months=1)).strftime('%Y-%m')

    target_orders = df[df['Date de commande'].dt.strftime('%Y-%m') == target_month]

    acquisition = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == target_month]
    nouveaux_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month]
    clients_recents = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
        [(pd.to_datetime(target_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(2, 6)]
    )]
    anciens_clients = target_orders[target_orders['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(target_month) - pd.DateOffset(months=5)).strftime('%Y-%m')]

    segment_counts = {
        'Segment': ['Acquisition', 'Nouveaux Clients', 'Clients Récents', 'Anciens Clients'],
        'Nombre de Clients': [len(acquisition['Restaurant ID'].unique()), len(nouveaux_clients['Restaurant ID'].unique()), len(clients_recents['Restaurant ID'].unique()), len(anciens_clients['Restaurant ID'].unique())],
        'Nombre de Clients Possible': [
            len(acquisition['Restaurant ID'].unique()),
            len(df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month)]['Restaurant ID'].unique()),
            len(df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
                [(pd.to_datetime(previous_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(1, 5)]
            ))]['Restaurant ID'].unique()),
            len(df[(df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=5)).strftime('%Y-%m'))]['Restaurant ID'].unique())
        ],
        'Nombre de Clients Actifs (Mois Précédent)': [
            0,
            len(df[(df['Date de commande'].dt.strftime('%Y-%m') == previous_month) & (df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') == previous_month)]['Restaurant ID'].unique()),
            len(df[(df['Date de commande'].dt.strftime('%Y-%m') == previous_month) & (df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m').isin(
                [(pd.to_datetime(previous_month) - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(1, 5)]
            ))]['Restaurant ID'].unique()),
            len(df[(df['Date de commande'].dt.strftime('%Y-%m') == previous_month) & (df['date 1ere commande (Restaurant)'].dt.strftime('%Y-%m') < (pd.to_datetime(previous_month) - pd.DateOffset(months=5)).strftime('%Y-%m'))]['Restaurant ID'].unique())
        ],
        'Rapport (%)': [0, 0, 0, 0]
    }
    
    return pd.DataFrame(segment_counts)

# Préparer les données pour la page Objectifs
def prepare_objectifs_data(historical_data, df, objectifs_precedents):
    recent_month = '2024-07'
    segments = ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']
    data = []

    for country, df_hist in historical_data.items():
        df_country = df[df['Pays'] == country]
        segments_data = calculate_segments_for_month(df_country, recent_month)
        for segment in segments:
            taux_2024 = 0
            if not objectifs_precedents.empty:
                taux_2024 = objectifs_precedents.loc[(objectifs_precedents['Pays'] == country) & (objectifs_precedents['Segment'] == segment), 'Taux 2024']
                if not taux_2024.empty:
                    taux_2024 = taux_2024.values[0]

            row = {
                'Pays': country,
                'Segment': segment,
                'Possible': segments_data[segments_data['Segment'] == segment]['Nombre de Clients Possible'].values[0],
                'Mois Dernier': segments_data[segments_data['Segment'] == segment]['Nombre de Clients Actifs (Mois Précédent)'].values[0],
                'Juillet NOW': segments_data[segments_data['Segment'] == segment]['Nombre de Clients'].values[0],
                'Taux 2023': calculate_repeat_rate_2023(historical_data, segment)[country],
                'Taux 2024': taux_2024,
                'OBJ Juillet': 0,
                'Reste à faire': 0
            }
            data.append(row)

    df_objectifs = pd.DataFrame(data)

    if not objectifs_precedents.empty:
        df_objectifs['OBJ Juillet'] = (df_objectifs['Mois Dernier'] * (df_objectifs['Taux 2024'] / 100)).astype(int)
        df_objectifs['Reste à faire'] = df_objectifs['OBJ Juillet'] - df_objectifs['Juillet NOW']

    # Ajouter une ligne de total
    total_row = pd.DataFrame({
        'Pays': ['Total'],
        'Segment': [''],
        'Possible': [df_objectifs['Possible'].sum()],
        'Mois Dernier': [df_objectifs['Mois Dernier'].sum()],
        'Juillet NOW': [df_objectifs['Juillet NOW'].sum()],
        'Taux 2023': [0],  # Non utilisé pour le total
        'Taux 2024': [0],  # Non utilisé pour le total
        'OBJ Juillet': [df_objectifs['OBJ Juillet'].sum()],
        'Reste à faire': [df_objectifs['Reste à faire'].sum()]
    })
    df_objectifs = pd.concat([df_objectifs, total_row], ignore_index=True)

    return df_objectifs

def calculate_repeat(df):
    df['Taux 2024'] = pd.to_numeric(df['Taux 2024'], errors='coerce').fillna(0)
    df['OBJ Juillet'] = (df['Mois Dernier'] * (df['Taux 2024'] / 100)).astype(int)
    df['Reste à faire'] = df['OBJ Juillet'] - df['Juillet NOW']
    return df

def update_totals(df):
    df.loc[df['Pays'] == 'Total', 'OBJ Juillet'] = df.loc[df['Pays'] != 'Total', 'OBJ Juillet'].sum()
    df.loc[df['Pays'] == 'Total', 'Reste à faire'] = df.loc[df['Pays'] != 'Total', 'Reste à faire'].sum()
    return df

def objectifs_page():
    st.title('Définir les Objectifs des Account Managers')

    # Charger les objectifs précédemment enregistrés
    db_gen = get_db()
    db = next(db_gen)
    try:
        objectifs_precedents = load_objectifs(db)
    except Exception as e:
        st.error(f"Erreur lors du chargement des objectifs: {e}")
        objectifs_precedents = pd.DataFrame()

    # Charger et traiter les données historiques et récentes
    historical_data = load_historical_data()
    df_recent = load_recent_data()
    df_recent = preprocess_data(df_recent)

    if 'df_objectifs' not in st.session_state:
        df_objectifs = prepare_objectifs_data(historical_data, df_recent, objectifs_precedents)
        st.session_state.df_objectifs = df_objectifs
    else:
        df_objectifs = st.session_state.df_objectifs

    # JavaScript pour recalculer automatiquement OBJ Juillet et Reste à faire
    js_code = JsCode("""
    function(params) {
        if (params.colDef.field === 'Taux 2024') {
            let taux2024 = params.newValue;
            let moisDernier = params.data['Mois Dernier'];
            params.data['OBJ Juillet'] = Math.round(moisDernier * (taux2024 / 100));
            params.data['Reste à faire'] = params.data['OBJ Juillet'] - params.data['Juillet NOW'];
            params.api.applyTransaction({update: [params.data]});

            // Update the total row
            let totalObjJuillet = 0;
            let totalResteAFaire = 0;
            params.api.forEachNode(function(rowNode) {
                if (rowNode.data.Pays !== 'Total') {
                    totalObjJuillet += rowNode.data['OBJ Juillet'];
                    totalResteAFaire += rowNode.data['Reste à faire'];
                }
            });
            let totalRow = params.api.getRowNode('Total');
            totalRow.setDataValue('OBJ Juillet', totalObjJuillet);
            totalRow.setDataValue('Reste à faire', totalResteAFaire);
        }
    }
    """)

    # Tableau interactif
    gb = GridOptionsBuilder.from_dataframe(st.session_state.df_objectifs)
    gb.configure_columns(["Pays", "Segment", "Possible", "Mois Dernier", "Juillet NOW", "Taux 2023", "OBJ Juillet", "Reste à faire"], editable=False)
    gb.configure_column("Taux 2024", editable=True, cellStyle=JsCode("""
    function(params) {
        return {
            'backgroundColor': 'yellow'
        }
    }
    """))
    gb.configure_grid_options(domLayout='normal', onCellValueChanged=js_code)

    grid_options = gb.build()
    grid_response = AgGrid(st.session_state.df_objectifs, gridOptions=grid_options, enable_enterprise_modules=True, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)
    updated_df = pd.DataFrame(grid_response['data'])

    # Mise à jour des données dans le session_state après modification
    st.session_state.df_objectifs.update(updated_df)

    # Bouton pour afficher le champ de mot de passe
    if 'show_password_field' not in st.session_state:
        st.session_state.show_password_field = False

    if st.button('Valider'):
        st.session_state.show_password_field = True

    if st.session_state.show_password_field:
        password = st.text_input('Entrez le mot de passe pour valider les objectifs:', type='password')
        if st.button('Confirmer'):
            if password == 'foodostreamlit':
                st.session_state.df_objectifs = calculate_repeat(st.session_state.df_objectifs)
                st.session_state.df_objectifs = update_totals(st.session_state.df_objectifs)
                st.success('Les objectifs ont été enregistrés.')
                total_clients_actifs = st.session_state.df_objectifs.loc[st.session_state.df_objectifs['Pays'] != 'Total', 'OBJ Juillet'].sum()
                st.info(f'Cela fait un total de {total_clients_actifs} clients actifs.')
                # Sauvegarder les objectifs dans la base de données
                try:
                    save_objectifs(db, st.session_state.df_objectifs)
                    st.success('Les objectifs ont été enregistrés dans la base de données.')
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement des objectifs: {e}")
                st.session_state.show_password_field = False
            else:
                st.error('Mot de passe incorrect.')

    # Afficher les objectifs précédemment enregistrés
    if not objectifs_precedents.empty:
        st.write('Objectifs précédemment enregistrés:')
        st.write(objectifs_precedents)

if __name__ == '__main__':
    objectifs_page()

