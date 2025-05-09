# import json

# def charger_reseau_syntaxique(nom_fichier):
#     with open(nom_fichier, 'r', encoding='utf-8') as f:
#         return json.load(f)

# def propagation_de_marqueurs(reseau, liste_node1, liste_node2, relation_visee, relations_a_suivre=None):
#     noeuds = reseau["nodes"]
#     arcs = reseau["edges"]
    
#     if relations_a_suivre is None:
#         relations_a_suivre = ["is a"]  # Par défaut, suit uniquement les relations "is a"

#     resultats = []

#     for i in range(len(liste_node1)):
#         M1 = next((n for n in noeuds if n["label"] == liste_node1[i]), None)
#         M2 = next((n for n in noeuds if n["label"] == liste_node2[i]), None)

#         if not M1 or not M2:
#             resultats.append(f"[✖] {liste_node1[i]} ou {liste_node2[i]} n'existe pas dans le réseau.")
#             continue

#         pile = [{"from": M1["id"], "chemin": [M1["label"]]}]
#         visites = set()
#         trouve = False

#         while pile:
#             courant = pile.pop()
#             courant_id = courant["from"]
#             chemin = courant["chemin"]

#             if courant_id in visites:
#                 continue
#             visites.add(courant_id)

#             # Vérifie s'il y a un lien direct vers le nœud cible avec la relation visée
#             for arc in arcs:
#                 if arc["from"] == courant_id and arc["to"] == M2["id"] and arc["label"] == relation_visee:
#                     chemin_complet = chemin + [M2["label"]]
#                     resultats.append(f"[✔] {' → '.join(chemin_complet)} ({relation_visee})")
#                     trouve = True
#                     break
#             if trouve:
#                 break

#             # Propage en suivant les relations spécifiées
#             for arc in arcs:
#                 if arc["from"] == courant_id and arc["label"] in relations_a_suivre:
#                     pile.append({
#                         "from": arc["to"],
#                         "chemin": chemin + [get_label(arc["to"], noeuds)]
#                     })

#         if not trouve:
#             resultats.append(f"[✖] Pas de relation '{relation_visee}' entre {liste_node1[i]} et {liste_node2[i]}")
            
#     return resultats  # Retourne la liste des résultats

# def get_label(node_id, noeuds):
#     node = next((n for n in noeuds if n["id"] == node_id), None)
#     return node["label"] if node else "???"

# def afficher_reseau(reseau):
#     print("\n=== STRUCTURE DU RÉSEAU ===")
#     print("\nNOEUDS:")
#     for node in reseau["nodes"]:
#         print(f"  ID: {node['id']} - Label: {node['label']}")
    
#     print("\nRELATIONS:")
#     relations = {}
#     for edge in reseau["edges"]:
#         relation = edge["label"]
#         if relation not in relations:
#             relations[relation] = []
#         from_label = get_label(edge["from"], reseau["nodes"])
#         to_label = get_label(edge["to"], reseau["nodes"])
#         relations[relation].append(f"{from_label} → {to_label}")
    
#     for relation, exemples in relations.items():
#         print(f"  {relation}:")
#         for exemple in exemples:
#             print(f"    {exemple}")

# if __name__ == "__main__":
#     nom_fichier = "reseau.json"  # remplace par ton fichier
#     reseau = charger_reseau_syntaxique(nom_fichier)
    
#     # Affiche la structure du réseau
#     afficher_reseau(reseau)

#     concepts1 = ["Logique D ordre 1", "Topologie"]
#     concepts2 = ["Systeme S5", "Mathematiques"]
#     relation = "is a"
#     relations_a_suivre = ["is a", "part of"]  # Suivre à la fois "is a" et "part of"

#     print("\n=== RÉSULTATS DE PROPAGATION ===")
#     resultats = propagation_de_marqueurs(reseau, concepts1, concepts2, relation, relations_a_suivre)
#     for ligne in resultats:
#         print(ligne)


import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def charger_reseau_syntaxique(nom_fichier):
    with open(nom_fichier, 'r', encoding='utf-8') as f:
        return json.load(f)

def propagation_de_marqueurs(reseau, liste_node1, liste_node2, relation_visee, relations_a_suivre=None):
    noeuds = reseau["nodes"]
    arcs = reseau["edges"]
    
    if relations_a_suivre is None:
        relations_a_suivre = ["is a"]  # Par défaut, suit uniquement les relations "is a"

    resultats = []

    for i in range(len(liste_node1)):
        M1 = next((n for n in noeuds if n["label"] == liste_node1[i]), None)
        M2 = next((n for n in noeuds if n["label"] == liste_node2[i]), None)

        if not M1 or not M2:
            resultats.append(f"[✖] {liste_node1[i]} ou {liste_node2[i]} n'existe pas dans le réseau.")
            continue

        pile = [{"from": M1["id"], "chemin": [M1["label"]]}]
        visites = set()
        trouve = False

        while pile:
            courant = pile.pop()
            courant_id = courant["from"]
            chemin = courant["chemin"]

            if courant_id in visites:
                continue
            visites.add(courant_id)

            # Vérifie s'il y a un lien direct vers le nœud cible avec la relation visée
            for arc in arcs:
                if arc["from"] == courant_id and arc["to"] == M2["id"] and arc["label"] == relation_visee:
                    chemin_complet = chemin + [M2["label"]]
                    resultats.append(f"[✔] {' → '.join(chemin_complet)} ({relation_visee})")
                    trouve = True
                    break
            if trouve:
                break

            # Propage en suivant les relations spécifiées
            for arc in arcs:
                if arc["from"] == courant_id and arc["label"] in relations_a_suivre:
                    pile.append({
                        "from": arc["to"],
                        "chemin": chemin + [obtenir_label(arc["to"], noeuds)]
                    })

        if not trouve:
            resultats.append(f"[✖] Pas de relation '{relation_visee}' entre {liste_node1[i]} et {liste_node2[i]}")
            
    return resultats  # Retourne la liste des résultats

def obtenir_label(noeud_id, noeuds):
    noeud = next((n for n in noeuds if n["id"] == noeud_id), None)
    return noeud["label"] if noeud else "???"

def afficher_reseau(reseau):
    print("\n=== STRUCTURE DU RÉSEAU ===")
    print("\nNOEUDS:")
    for noeud in reseau["nodes"]:
        print(f"  ID: {noeud['id']} - Label: {noeud['label']}")
    
    print("\nRELATIONS:")
    relations = {}
    for arc in reseau["edges"]:
        relation = arc["label"]
        if relation not in relations:
            relations[relation] = []
        de_label = obtenir_label(arc["from"], reseau["nodes"])
        vers_label = obtenir_label(arc["to"], reseau["nodes"])
        relations[relation].append(f"{de_label} → {vers_label}")
    
    for relation, exemples in relations.items():
        print(f"  {relation}:")
        for exemple in exemples:
            print(f"    {exemple}")

def visualiser_reseau(reseau):
    """
    Visualise le réseau sémantique avec matplotlib et networkx
    """
    # Créer un graphe dirigé
    G = nx.DiGraph()
    
    # Ajouter les nœuds
    for noeud in reseau["nodes"]:
        G.add_node(noeud["id"], label=noeud["label"])
    
    # Ajouter les arêtes avec leurs labels
    for arc in reseau["edges"]:
        G.add_edge(arc["from"], arc["to"], label=arc["label"])
    
    # Créer la figure
    plt.figure(figsize=(12, 10))
    
    # Définir le layout (positionnement des nœuds)
    pos = nx.spring_layout(G, seed=42, k=0.9)  # k contrôle l'espacement
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=700, alpha=0.8)
    
    # Dessiner les labels des nœuds
    labels_noeuds = {noeud_id: G.nodes[noeud_id]['label'] for noeud_id in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels_noeuds, font_size=10)
    
    # Dessiner les arêtes avec des flèches
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7, 
                          arrowsize=15, arrowstyle='->', edge_color='gray')
    
    # Ajouter les labels des relations
    labels_arcs = {(u, v): G.edges[u, v]['label'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_arcs, 
                                font_size=8, font_color='red')
    
    # Ajouter un titre
    plt.title("Réseau Sémantique", fontsize=15)
    
    # Supprimer les axes
    plt.axis('off')
    
    # Ajuster le layout
    plt.tight_layout()
    
    # Afficher le graphe
    plt.show()

if __name__ == "__main__":
    nom_fichier = "reseau.json"  # remplace par ton fichier
    reseau = charger_reseau_syntaxique(nom_fichier)
    
    # Affiche la structure du réseau
    afficher_reseau(reseau)
    
    # Visualisation graphique du réseau
    visualiser_reseau(reseau)

    concepts1 = ["Logique D ordre 1", "Topologie"]
    concepts2 = ["Systeme S5", "Mathematiques"]
    relation = "is a"
    relations_a_suivre = ["is a", "part of"]  # Suivre à la fois "is a" et "part of"

    print("\n=== RÉSULTATS DE PROPAGATION ===")
    resultats = propagation_de_marqueurs(reseau, concepts1, concepts2, relation, relations_a_suivre)
    for ligne in resultats:
        print(ligne)