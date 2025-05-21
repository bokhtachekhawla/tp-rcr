import json
import matplotlib.pyplot as plt
import networkx as nx

def charger_reseau_syntaxique(nom_fichier):
    """Charge un réseau sémantique à partir d'un fichier JSON"""
    with open(nom_fichier, 'r', encoding='utf-8') as f:
        return json.load(f)

def obtenir_label(noeud_id, noeuds):
    """Récupère le label d'un nœud à partir de son ID"""
    noeud = next((n for n in noeuds if n["id"] == noeud_id), None)
    return noeud["label"] if noeud else "???"

def afficher_reseau(reseau):
    """Affiche la structure du réseau dans la console"""
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

def visualiser_reseau_avec_exceptions(reseau):
    """Visualise le réseau sémantique avec matplotlib et networkx en mettant en évidence les exceptions"""
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
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700, alpha=0.8)
    
    # Dessiner les labels des nœuds
    labels_noeuds = {noeud_id: G.nodes[noeud_id]['label'] for noeud_id in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels_noeuds, font_size=10)
    
    # Séparer les arêtes normales et les exceptions
    edges_normal = [(u, v) for u, v in G.edges() if G.edges[u, v]['label'] != "exception"]
    edges_exception = [(u, v) for u, v in G.edges() if G.edges[u, v]['label'] == "exception"]
    
    # Dessiner les arêtes normales
    nx.draw_networkx_edges(G, pos, edgelist=edges_normal, width=1.0, alpha=0.7, 
                          arrowsize=15, arrowstyle='->', edge_color='gray')
    
    # Dessiner les arêtes d'exception en rouge
    nx.draw_networkx_edges(G, pos, edgelist=edges_exception, width=2.0, alpha=0.9, 
                          arrowsize=20, arrowstyle='->', edge_color='red')
    
    # Ajouter les labels des relations
    labels_arcs = {(u, v): G.edges[u, v]['label'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_arcs, font_size=8, font_color='red')
    
    # Ajouter une légende
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1, label='Relation normale'),
        Line2D([0], [0], color='red', lw=2, label='Exception')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Ajouter un titre
    plt.title("Réseau Sémantique avec Exceptions", fontsize=15)
    
    # Supprimer les axes
    plt.axis('off')
    
    # Ajuster le layout
    plt.tight_layout()
    
    # Afficher le graphe
    plt.show()

def ajouter_exception(reseau, noeud_source, noeud_cible):
    """Ajoute une relation d'exception entre deux nœuds"""
    noeuds = reseau["nodes"]
    
    source = next((n for n in noeuds if n["label"] == noeud_source), None)
    cible = next((n for n in noeuds if n["label"] == noeud_cible), None)
    
    if not source or not cible:
        print(f"Erreur: Un des nœuds spécifiés n'existe pas dans le réseau.")
        return reseau
    
    # Vérifier si l'exception existe déjà
    if any(arc["from"] == source["id"] and arc["to"] == cible["id"] and arc["label"] == "exception" 
           for arc in reseau["edges"]):
        print(f"L'exception entre {noeud_source} et {noeud_cible} existe déjà.")
        return reseau
    
    # Ajouter la nouvelle exception
    reseau["edges"].append({
        "from": source["id"],
        "to": cible["id"],
        "label": "exception"
    })
    
    print(f"Exception ajoutée: {noeud_source} → {noeud_cible}")
    return reseau

def propagation_avec_exceptions(reseau, noeuds_source, noeuds_cible, relation_visee, relations_a_suivre=None, relation_exception="exception"):
    """
    Algorithme de propagation qui tient compte des liens d'exception.
    
    Args:
        reseau: Le réseau sémantique
        noeuds_source: Liste des nœuds source
        noeuds_cible: Liste des nœuds cible
        relation_visee: Relation à vérifier
        relations_a_suivre: Relations à suivre lors de la propagation
        relation_exception: Label de la relation d'exception
        
    Returns:
        Liste des résultats de propagation en tenant compte des exceptions
    """
    noeuds = reseau["nodes"]
    arcs = reseau["edges"]
    
    if relations_a_suivre is None:
        relations_a_suivre = ["is a"]  # Par défaut, suit uniquement les relations "is a"

    resultats = []

    for i in range(len(noeuds_source)):
        M1 = next((n for n in noeuds if n["label"] == noeuds_source[i]), None)
        M2 = next((n for n in noeuds if n["label"] == noeuds_cible[i]), None)

        if not M1 or not M2:
            resultats.append(f"[✖] {noeuds_source[i]} ou {noeuds_cible[i]} n'existe pas dans le réseau.")
            continue

        # Vérifier d'abord s'il existe une exception directe
        exception_directe = any(
            arc["from"] == M1["id"] and arc["to"] == M2["id"] and arc["label"] == relation_exception 
            for arc in arcs
        )
        
        if exception_directe:
            resultats.append(f"[✖] Exception directe: {noeuds_source[i]} ne peut pas être relié à {noeuds_cible[i]} ({relation_visee})")
            continue
        
        # Structure pour la traversée du réseau
        pile = [{"from": M1["id"], "chemin": [M1["label"]]}]
        visites = set()
        trouve = False
        exceptions = []  # Pour stocker les exceptions rencontrées

        while pile and not trouve:
            courant = pile.pop()
            courant_id = courant["from"]
            chemin = courant["chemin"]

            if courant_id in visites:
                continue
            visites.add(courant_id)
            
            # Vérifier si le nœud courant a une exception pour ce type de relation avec la cible
            a_exception = any(
                arc["from"] == courant_id and arc["to"] == M2["id"] and arc["label"] == relation_exception
                for arc in arcs
            )
            
            if a_exception:
                noeud_courant = obtenir_label(courant_id, noeuds)
                exceptions.append(f"{noeud_courant} → {noeuds_cible[i]}")
                continue  # Ne pas explorer ce chemin plus loin
            
            # Vérifier s'il y a un lien direct vers le nœud cible avec la relation visée
            for arc in arcs:
                if arc["from"] == courant_id and arc["to"] == M2["id"] and arc["label"] == relation_visee:
                    # Vérifier s'il existe une exception pour cette relation
                    exception_existe = False
                    
                    # Parcourir la hiérarchie pour vérifier les exceptions
                    noeud_actuel_id = courant_id
                    while not exception_existe:
                        # Vérifier l'exception directe pour ce nœud
                        if any(a["from"] == noeud_actuel_id and a["to"] == M2["id"] and a["label"] == relation_exception for a in arcs):
                            exception_existe = True
                            break
                        
                        # Remonter aux parents s'il y en a
                        parents = [a["to"] for a in arcs if a["from"] == noeud_actuel_id and a["label"] == "is a"]
                        if not parents:
                            break
                        
                        noeud_actuel_id = parents[0]  # Prendre le premier parent
                    
                    if not exception_existe:
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
            message = f"[✖] Pas de relation '{relation_visee}' entre {noeuds_source[i]} et {noeuds_cible[i]}"
            if exceptions:
                message += f" (Exceptions trouvées: {', '.join(exceptions)})"
            resultats.append(message)
            
    return resultats

if __name__ == "__main__":
    print("=== ALGORITHME DE PROPAGATION AVEC EXCEPTIONS ===")
    
    try:
        nom_fichier = "reseau.json"
        reseau = charger_reseau_syntaxique(nom_fichier)
        
        # Afficher la structure du réseau
        afficher_reseau(reseau)
        
        # Ajouter des exceptions au réseau pour les tests
        print("\n=== AJOUT D'EXCEPTIONS AU RÉSEAU ===")
        reseau = ajouter_exception(reseau, "Logique D ordre 1", "Systeme S5")
        reseau = ajouter_exception(reseau, "Logique Modale", "Logique Classique")
        
        # Afficher le réseau avec les exceptions
        print("\n=== STRUCTURE DU RÉSEAU AVEC EXCEPTIONS ===")
        relations_exceptions = [arc for arc in reseau["edges"] if arc["label"] == "exception"]
        for arc in relations_exceptions:
            de_label = obtenir_label(arc["from"], reseau["nodes"])
            vers_label = obtenir_label(arc["to"], reseau["nodes"])
            print(f"  Exception: {de_label} → {vers_label}")
        
        print("\n=== DÉMONSTRATION DE PROPAGATION AVEC EXCEPTIONS ===")
        
        # Test 1: Vérifier une relation directe avec exception
        print("\n1. Vérification avec exception directe:")
        concepts1 = ["Logique D ordre 1"]
        concepts2 = ["Systeme S5"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "is a", ["is a"])
        for ligne in resultats:
            print(ligne)
        
        # Test 2: Vérifier une relation sans exception
        print("\n2. Vérification sans exception:")
        concepts1 = ["Systeme S5"]
        concepts2 = ["Logique Modale"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "is a", ["is a"])
        for ligne in resultats:
            print(ligne)
        
        # Test 3: Vérifier une relation avec exception indirecte
        print("\n3. Vérification avec exception indirecte:")
        concepts1 = ["Systeme K"]
        concepts2 = ["Logique Classique"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "derived_from", ["is a", "derived_from"])
        for ligne in resultats:
            print(ligne)
            
        # Visualiser le réseau avec les exceptions
        print("\nAffichage de la visualisation graphique du réseau avec exceptions...")
        visualiser_reseau_avec_exceptions(reseau)
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier 'reseau.json' n'a pas été trouvé.")
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier JSON n'est pas correctement formaté.")
    except Exception as e:
        print(f"Erreur: {str(e)}")