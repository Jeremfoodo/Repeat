def objectifs_page(df):
    st.title('Définir les Objectifs de Clients Actifs pour Juillet 2024')

    # Récupérer les objectifs enregistrés
    objectifs = get_objectifs()

    # Filtrer les pays pertinents
    countries = ['FR', 'BE', 'GB', 'US']
    segments = ['Nouveaux Clients', 'Clients Récents', 'Anciens Clients']

    if objectifs:
        st.header('Objectifs Actuels')
        rows = []
        for objectif in objectifs:
            id, pays, segment, obj = objectif
            if pays in countries:  # Vérifiez si 'pays' est parmi les pays pertinents
                rows.append({'Pays': pays, 'Segment': segment, 'Objectif': obj})
        objectifs_df = pd.DataFrame(rows)
        st.dataframe(objectifs_df)

        st.header('Modifier les Objectifs')
        with st.form(key='objectifs_form'):
            st.write('Entrer les objectifs par segment et par pays')
            objectif_data = []
            for country in countries:
                for segment in segments:
                    objectif = st.number_input(f'Objectif {segment} pour {country}', min_value=0, step=1)
                    objectif_data.append((country, segment, objectif))

            code = st.text_input('Code de validation')
            submit_button = st.form_submit_button(label='Enregistrer les Objectifs')

            if submit_button:
                if code == 'Inesqueenofrepeat':
                    for country, segment, objectif in objectif_data:
                        save_objectif(country, segment, objectif)
                    st.success('Objectifs enregistrés avec succès!')
                    st.experimental_rerun()
                else:
                    st.error('Code de validation incorrect')

        st.header('Objectifs Actuels et Écarts')
        active_clients = get_active_clients(df, '2024-07')

        rows = []
        for objectif in objectifs:
            id, pays, segment, obj = objectif
            if pays in countries:  # Vérifiez si 'pays' est parmi les pays pertinents
                actuel = active_clients.get(pays, {}).get(segment, 0)
                ecart = obj - actuel
                rows.append({'Pays': pays, 'Segment': segment, 'Objectif': obj, 'Actuel': actuel, 'Écart': ecart})

        objectifs_df = pd.DataFrame(rows)
        st.dataframe(objectifs_df)

        # Bouton de téléchargement
        csv = objectifs_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger les objectifs en CSV",
            data=csv,
            file_name='objectifs_clients_actifs.csv',
            mime='text/csv',
        )

    else:
        st.write("Aucun objectif enregistré.")
        with st.form(key='objectifs_form'):
            st.write('Entrer les objectifs par segment et par pays')
            objectif_data = []
            for country in countries:
                for segment in segments:
                    objectif = st.number_input(f'Objectif {segment} pour {country}', min_value=0, step=1)
                    objectif_data.append((country, segment, objectif))

            code = st.text_input('Code de validation')
            submit_button = st.form_submit_button(label='Enregistrer les Objectifs')

            if submit_button:
                if code == 'Inesqueenofrepeat':
                    for country, segment, objectif in objectif_data:
                        save_objectif(country, segment, objectif)
                    st.success('Objectifs enregistrés avec succès!')
                    st.experimental_rerun()
                else:
                    st.error('Code de validation incorrect')
