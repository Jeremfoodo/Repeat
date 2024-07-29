import plotly.express as px
import pandas as pd

def plot_ratios(segment, all_results, country_code):
    if country_code == 'Global':
        year_results = all_results[all_results['Mois'].str.startswith('2023')]
    else:
        year_results = all_results[(all_results['Mois'].str.startswith('2023')) & (all_results['Pays'] == country_code)]

    ratios = year_results[year_results['Segment'] == segment]
    
    fig = px.line(ratios, x='Mois', y='Rapport (%)', title=f'{segment} - {country_code} - Taux de Repeat', markers=True)
    fig.update_layout(yaxis_tickformat='%')
    return fig
