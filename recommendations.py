# recommendations.py
from datetime import datetime
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

def get_recommendations(client_recent_purchases, client_june_data, client_july_data, df_recent_purchases, segmentation_df, client_id):
    recommendations = []

    # Comparer les dépenses entre juin et juillet
    june_spending = client_june_data['GMV'].sum()
    july_spending = client_july_data['GMV'].sum()

    if july_spending < june_spending:
        recommendations.append({
            "Type": "Augmentation des efforts",
            "Recommandation": "Le client a baissé ses dépenses en juillet par rapport à juin. Augmentez les efforts de recommandation pour l'inciter à commander plus.",
            "Détails": ""
        })
    elif july_spending > june_spending:
        recommendations.append({
            "Type": "Maintien des efforts",
            "Recommandation": "Le client a augmenté ses dépenses en juillet par rapport à juin. Maintenez ou améliorez les recommandations pour continuer cette tendance.",
            "Détails": ""
        })

    # Fréquence d'achat
    if 'Fruits et Légumes' in client_recent_purchases['Product Category'].values:
        last_fruit_veg_order_date = client_recent_purchases[client_recent_purchases['Product Category'] == 'Fruits et Légumes']['Date'].max()
        last_fruit_veg_order_date = pd.to_datetime(last_fruit_veg_order_date, errors='coerce')
        if (datetime.now() - last_fruit_veg_order_date).days > 7:
            recommendations.append({
                "Type": "Rachat de fruits et légumes",
                "Recommandation": "Recommandez de racheter des fruits et légumes.",
                "Détails": f"Le dernier achat de fruits et légumes a été effectué il y a {(datetime.now() - last_fruit_veg_order_date).days} jours."
            })
    else:
        last_order_date = client_recent_purchases['Date'].max()
        last_order_date = pd.to_datetime(last_order_date, errors='coerce')
        if (datetime.now() - last_order_date).days > 15:
            recommendations.append({
                "Type": "Rachat dans d'autres catégories",
                "Recommandation": "Recommandez de racheter dans d'autres catégories.",
                "Détails": f"Le dernier achat a été effectué il y a {(datetime.now() - last_order_date).days} jours."
            })

    # Nombre de catégories
    june_categories = client_june_data['Product Category'].nunique()
    july_categories = client_july_data['Product Category'].nunique()

    # Comparaison juin vs juillet
    if july_categories < june_categories:
        categories_not_bought_in_july = set(client_june_data['Product Category'].unique()) - set(client_july_data['Product Category'].unique())
        recommendations.append({
            "Type": "Recommandation de catégories",
            "Recommandation": "Recommandez des achats dans les catégories non commandées en juillet.",
            "Détails": f"Catégories non commandées en juillet: {', '.join(categories_not_bought_in_july)}"
        })

    # Nombre total de catégories distinctes
    total_categories = client_recent_purchases['Product Category'].nunique()

    if total_categories < 3:
        categories_to_recommend = ["Boucherie", "Fruits et Légumes", "Crémerie", "Epicerie Salée"]
        categories_not_bought = [cat for cat in categories_to_recommend if cat not in client_recent_purchases['Product Category'].values]
        recommendations.append({
            "Type": "Recommandation multicatégorie",
            "Recommandation": f"Le client ne commande que dans {total_categories} catégorie(s). Faites du cross !",
            "Détails": f"Catégories à recommander: {', '.join(categories_not_bought)}"
        })
    elif total_categories >= 3:
        recommendations.append({
            "Type": "Augmentation des produits",
            "Recommandation": "Focalisez sur l'augmentation du nombre de produits ou des produits plus chers dans les catégories existantes.",
            "Détails": ""
        })

    # Produits fréquemment achetés mais récemment non commandés
    frequently_bought_products = client_recent_purchases.groupby('product_name').size().reset_index(name='counts').sort_values(by='counts', ascending=False)
    for product in frequently_bought_products['product_name'].unique():
        last_product_order_date = client_recent_purchases[client_recent_purchases['product_name'] == product]['Date'].max()
        last_product_order_date = pd.to_datetime(last_product_order_date, errors='coerce')
        if (datetime.now() - last_product_order_date).days > 30:
            recommendations.append({
                "Type": "Rachat de produit",
                "Recommandation": f"Recommandez de racheter le produit {product}.",
                "Détails": f"Le dernier achat de ce produit a été effectué il y a {(datetime.now() - last_product_order_date).days} jours."
            })

    # Recommandations basées sur les restaurants similaires
    client_info = segmentation_df[segmentation_df['Restaurant_id'] == client_id].iloc[0]
    similar_restaurants = segmentation_df[(segmentation_df['Gamme'] == client_info['Gamme']) & (segmentation_df['Type'] == client_info['Type'])]
    similar_restaurant_ids = similar_restaurants['Restaurant_id'].tolist()
    similar_purchases = df_recent_purchases[df_recent_purchases['Restaurant_id'].isin(similar_restaurant_ids)]

    # Appliquer l'algorithme Apriori
    basket = similar_purchases.groupby(['Restaurant_id', 'product_name'])['GMV'].sum().unstack().reset_index().fillna(0).set_index('Restaurant_id')
    basket_sets = basket.applymap(lambda x: 1 if x > 0 else 0)
    frequent_itemsets = apriori(basket_sets, min_support=0.05, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

    # Trier les produits recommandés par support
    top_recommendations = rules.sort_values(by='support', ascending=False).head(10)

    # Formater les recommandations
    product_recommendations = []
    for _, row in top_recommendations.iterrows():
        product = list(row['antecedents'])[0]
        support = row['support']
        product_category = similar_purchases[similar_purchases['product_name'] == product]['Product Category'].iloc[0]
        product_recommendations.append({
            "Produit": product,
            "Catégorie": product_category,
            "Support (%)": round(support * 100, 2)
        })

    recommendations.append({
        "Type": "Recommandation basée sur les restaurants similaires",
        "Recommandation": "Les clients similaires (même gamme, même type) que ce client achètent ces produits en priorité :",
        "Détails": product_recommendations
    })
    
    return recommendations
