import plotly.graph_objs as go
import pandas as pd
import numpy as np

def plot_ratios(segment, all_results, country_code):
    years = [2022, 2023, 2024]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig = go.Figure()

    for year in years:
        if country_code == 'Global':
            year_results = all_results[all_results['Mois'].str.startswith(str(year))]
        else:
            year_results = all_results[(all_results['Mois'].str.startswith(str(year))) & (all_results['Pays'] == country_code)]
        
        ratios = year_results[year_results['Segment'] == segment]

        # Débogage : Vérification des résultats pour chaque année, segment et pays
        print(f"Année: {year}, Segment: {segment}, Pays: {country_code}")
        print(ratios)

        # Convert 'Mois' to month name and create a dictionary of ratios
        ratios_dict = {pd.to_datetime(row['Mois']).strftime('%b'): row['Rapport (%)'] for _, row in ratios.iterrows()}
        full_ratios = [ratios_dict.get(month, np.nan) for month in months]

        fig.add_trace(go.Scatter(x=months, y=full_ratios, mode='lines+markers', name=f'{year}'))

        if year == 2024:
            for i, txt in enumerate(full_ratios):
                if not pd.isna(txt):
                    fig.add_annotation(x=months[i], y=full_ratios[i], text=str(txt), showarrow=True, arrowhead=2)

    fig.update_layout(
        title=f'Évolution de la Rétention des {segment} - {country_code}',
        xaxis_title='Mois',
        yaxis_title='Rapport (%)',
        legend_title='Année',
        template='plotly_white'
    )
    return fig
