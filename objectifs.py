import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from db import SessionLocal, Objectif
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def load_objectifs(db: Session):
    objectifs = db.query(Objectif).all()
    return pd.DataFrame([o.__dict__ for o in objectifs])

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

def prepare_initial_data():
    # Remplacez cette fonction par la génération initiale de vos données
    data = [
        {"Pays": "FR", "Segment": "Nouveaux Clients", "Possible": 100, "Mois Dernier": 90, "Juillet NOW": 80, "Taux 2023": 50.0, "Taux 2024": 0.0, "OBJ Juillet": 0, "Reste à faire": 0},
        {"Pays": "US", "Segment": "Clients Récents", "Possible": 200, "Mois Dernier": 180, "Juillet NOW": 160, "Taux 2023": 60.0, "Taux 2024": 0.0, "OBJ Juillet": 0, "Reste à faire": 0},
        {"Pays": "BE", "Segment": "Anciens Clients", "Possible": 150, "Mois Dernier": 140, "Juillet NOW": 130, "Taux 2023": 40.0, "Taux 2024": 0.0, "OBJ Juillet": 0, "Reste à faire": 0},
        {"Pays": "GB", "Segment": "Nouveaux Clients", "Possible": 120, "Mois Dernier": 110, "Juillet NOW": 100, "Taux 2023": 55.0, "Taux 2024": 0.0, "OBJ Juillet": 0, "Reste à faire": 0},
    ]
    return pd.DataFrame(data)

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

    db = next(get_db())

    if 'df_objectifs' not in st.session_state:
        df_objectifs = load_objectifs(db)
        if df_objectifs.empty:
            df_objectifs = prepare_initial_data()
        st.session_state.df_objectifs = df_objectifs

    df = st.session_state.df_objectifs

    # Afficher le tableau interactif et permettre la modification des taux 2024
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_columns(["Pays", "Segment", "Possible", "Mois Dernier", "Juillet NOW", "Taux 2023", "OBJ Juillet", "Reste à faire"], editable=False)
    gb.configure_column("Taux 2024", editable=True, cellStyle=JsCode("""
    function(params) {
        return {
            'backgroundColor': 'yellow'
        }
    }
    """))

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

    gb.configure_grid_options(domLayout='normal', onCellValueChanged=js_code)

    grid_options = gb.build()
    grid_response = AgGrid(df, gridOptions=grid_options, enable_enterprise_modules=True, fit_columns_on_grid_load=True, allow_unsafe_jscode=True)
    updated_df = pd.DataFrame(grid_response['data'])

    st.session_state.df_objectifs.update(updated_df)

    if st.button('Valider'):
        password = st.text_input('Entrez le mot de passe pour valider les objectifs:', type='password')
        if st.button('Confirmer'):
            if password == 'foodostreamlit':
                st.session_state.df_objectifs = calculate_repeat(st.session_state.df_objectifs)
                st.session_state.df_objectifs = update_totals(st.session_state.df_objectifs)
                save_objectifs(db, st.session_state.df_objectifs)
                st.success('Les objectifs ont été enregistrés.')
                total_clients_actifs = st.session_state.df_objectifs.loc[st.session_state.df_objectifs['Pays'] != 'Total', 'OBJ Juillet'].sum()
                st.info(f'Cela fait un total de {total_clients_actifs} clients actifs.')
            else:
                st.error('Mot de passe incorrect.')

if __name__ == '__main__':
    objectifs_page()
