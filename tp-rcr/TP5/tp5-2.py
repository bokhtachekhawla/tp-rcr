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

def est_exception(arc):
    """Détermine si un arc représente une exception"""
    return arc.get("edge_type") == "exception"

def visualiser_reseau(reseau):
    """Visualise le réseau sémantique avec matplotlib et networkx, en distinguant les exceptions"""
    # Créer un graphe dirigé
    G = nx.DiGraph()
    
    # Ajouter les nœuds
    for noeud in reseau["nodes"]:
        G.add_node(noeud["id"], label=noeud["label"])
    
    # Ajouter les arêtes avec leurs labels
    for arc in reseau["edges"]:
        # Utiliser une couleur différente pour les arcs d'exception et inférés
        if est_exception(arc):
            G.add_edge(arc["from"], arc["to"], label=arc["label"], inferred=False, exception=True)
        elif "inferred" in arc and arc["inferred"]:
            G.add_edge(arc["from"], arc["to"], label=arc["label"], inferred=True, exception=False)
        else:
            G.add_edge(arc["from"], arc["to"], label=arc["label"], inferred=False, exception=False)
    
    # Créer la figure
    plt.figure(figsize=(12, 10))
    
    # Définir le layout (positionnement des nœuds)
    pos = nx.spring_layout(G, seed=42, k=0.9)  # k contrôle l'espacement
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700, alpha=0.8)
    
    # Dessiner les labels des nœuds
    labels_noeuds = {noeud_id: G.nodes[noeud_id]['label'] for noeud_id in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels_noeuds, font_size=10)
    
    # Dessiner les arêtes avec des flèches (relations originales)
    normal_edges = [(u, v) for u, v in G.edges() if not G.edges[u, v]['inferred'] and not G.edges[u, v]['exception']]
    nx.draw_networkx_edges(G, pos, edgelist=normal_edges, width=1.0, alpha=0.7, 
                          arrowsize=15, arrowstyle='->', edge_color='gray')
    
    # Dessiner les arêtes inférées avec une couleur différente
    inferred_edges = [(u, v) for u, v in G.edges() if G.edges[u, v]['inferred']]
    nx.draw_networkx_edges(G, pos, edgelist=inferred_edges, width=1.0, alpha=0.7, 
                          arrowsize=15, arrowstyle='->', edge_color='blue', style='dashed')
    
    # Dessiner les arêtes d'exception en rouge
    exception_edges = [(u, v) for u, v in G.edges() if G.edges[u, v]['exception']]
    nx.draw_networkx_edges(G, pos, edgelist=exception_edges, width=2.0, alpha=0.9, 
                          arrowsize=20, arrowstyle='->', edge_color='red')
    
    # Ajouter les labels des relations
    labels_arcs = {(u, v): G.edges[u, v]['label'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_arcs, font_size=8, font_color='red')
    
    # Ajouter une légende
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1, label='Relation normale'),
        Line2D([0], [0], color='blue', lw=1, linestyle='--', label='Relation inférée'),
        Line2D([0], [0], color='red', lw=2, label='Exception')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Ajouter un titre
    plt.title("Réseau Sémantique d'Animaux avec Exceptions et Héritage", fontsize=15)
    
    # Supprimer les axes
    plt.axis('off')
    
    # Ajuster le layout
    plt.tight_layout()
    
    # Afficher le graphe
    plt.show()

def algorithme_heritage_avec_exceptions(reseau, noeud_cible=None, saturer_reseau=False):
    """
    Algorithme d'héritage qui tient compte des exceptions.
    
    Args:
        reseau: Le réseau sémantique
        noeud_cible: Le nœud dont on veut déduire les propriétés
        saturer_reseau: Si True, sature le réseau en inférant toutes les relations possibles
    
    Returns:
        Un dictionnaire des propriétés héritées par nœud ou le réseau saturé
    """
    noeuds = reseau["nodes"]
    arcs = reseau["edges"]
    
    # Fonction pour trouver tous les parents d'un nœud (relations "est un")
    def trouver_parents(noeud_id):
        parents = []
        for arc in arcs:
            if arc["from"] == noeud_id and arc["label"] == "est un":
                parents.append(arc["to"])
        return parents
    
    # Fonction pour trouver toutes les propriétés directes d'un nœud
    def trouver_proprietes_directes(noeud_id):
        proprietes = {}
        for arc in arcs:
            if arc["from"] == noeud_id and arc["label"] != "est un":
                if arc["label"] not in proprietes:
                    proprietes[arc["label"]] = []
                proprietes[arc["label"]].append(arc["to"])
        return proprietes
    
    # Fonction pour trouver les exceptions d'un nœud pour une propriété spécifique
    def a_exception(noeud_id, relation, cible_id):
        return any(arc["from"] == noeud_id and arc["to"] == cible_id and 
                  arc["label"] == relation and est_exception(arc) for arc in arcs)
    
    # Fonction récursive pour hériter des propriétés en tenant compte des exceptions
    def heriter_proprietes(noeud_id, proprietes_heritees=None, visites=None):
        if proprietes_heritees is None:
            proprietes_heritees = {}
        if visites is None:
            visites = set()
            
        if noeud_id in visites:  # Éviter les cycles
            return proprietes_heritees
        
        visites.add(noeud_id)
        
        # Ajouter les propriétés directes non exceptionnelles
        proprietes_directes = trouver_proprietes_directes(noeud_id)
        for relation, valeurs in proprietes_directes.items():
            if relation not in proprietes_heritees:
                proprietes_heritees[relation] = []
            for valeur in valeurs:
                # Ne pas ajouter si c'est une exception
                if not est_exception(next((arc for arc in arcs if arc["from"] == noeud_id and 
                                         arc["to"] == valeur and arc["label"] == relation), {})):
                    if valeur not in proprietes_heritees[relation]:
                        proprietes_heritees[relation].append(valeur)
        
        # Hériter des propriétés des parents (sauf celles avec exceptions)
        parents = trouver_parents(noeud_id)
        for parent_id in parents:
            parent_props = heriter_proprietes(parent_id, {}, visites.copy())
            
            for relation, valeurs in parent_props.items():
                if relation not in proprietes_heritees:
                    proprietes_heritees[relation] = []
                    
                for valeur in valeurs:
                    # Ne pas hériter si ce nœud a une exception pour cette propriété
                    if not a_exception(noeud_id, relation, valeur):
                        if valeur not in proprietes_heritees[relation]:
                            proprietes_heritees[relation].append(valeur)
            
        return proprietes_heritees
    
    # Mode 1: Déduire les propriétés d'un nœud spécifique
    if noeud_cible and not saturer_reseau:
        noeud = next((n for n in noeuds if n["label"] == noeud_cible), None)
        if not noeud:
            return {"erreur": f"Le nœud '{noeud_cible}' n'existe pas dans le réseau."}
        
        proprietes_heritees = heriter_proprietes(noeud["id"])
        
        # Convertir les IDs de nœuds en labels pour la lisibilité
        resultat = {}
        for relation, valeurs in proprietes_heritees.items():
            resultat[relation] = [obtenir_label(val, noeuds) for val in valeurs]
            
        return {"noeud": noeud_cible, "proprietes": resultat}
    
    # Mode 2: Saturer le réseau
    elif saturer_reseau:
        reseau_sature = {
            "nodes": noeuds.copy(),
            "edges": arcs.copy()
        }
        
        # Pour chaque nœud, déduire toutes ses propriétés héritées
        for noeud in noeuds:
            proprietes_heritees = heriter_proprietes(noeud["id"])
            
            # Ajouter les arcs inférés au réseau
            for relation, valeurs in proprietes_heritees.items():
                for valeur in valeurs:
                    # Vérifier si cette relation n'existe pas déjà directement
                    if not any(arc["from"] == noeud["id"] and arc["to"] == valeur and arc["label"] == relation for arc in reseau_sature["edges"]):
                        # Ajouter un nouvel arc inféré
                        nouvel_arc = {
                            "from": noeud["id"],
                            "to": valeur,
                            "label": relation,
                            "inferred": True  # Marquer comme inféré
                        }
                        reseau_sature["edges"].append(nouvel_arc)
        
        return reseau_sature
    
    # Mode 3: Déduire les propriétés pour tous les nœuds
    else:
        resultats = {}
        for noeud in noeuds:
            proprietes_heritees = heriter_proprietes(noeud["id"])
            
            # Convertir les IDs de nœuds en labels pour la lisibilité
            resultat = {}
            for relation, valeurs in proprietes_heritees.items():
                resultat[relation] = [obtenir_label(val, noeuds) for val in valeurs]
                
            resultats[noeud["label"]] = resultat
            
        return resultats

if __name__ == "__main__":
    print("=== ALGORITHME D'HÉRITAGE AVEC EXCEPTIONS - RÉSEAU D'ANIMAUX ===")
    
    try:
        nom_fichier = "reseau-exec.json"
        reseau = charger_reseau_syntaxique(nom_fichier)
        
        # Afficher la structure du réseau
        afficher_reseau(reseau)
        
        # Afficher les exceptions existantes dans le réseau
        print("\n=== EXCEPTIONS PRÉSENTES DANS LE RÉSEAU ===")
        exceptions = [arc for arc in reseau["edges"] if est_exception(arc)]
        for arc in exceptions:
            de_label = obtenir_label(arc["from"], reseau["nodes"])
            vers_label = obtenir_label(arc["to"], reseau["nodes"])
            print(f"  Exception: {de_label} → {vers_label} ({arc['label']})")
        
        print("\n=== DÉMONSTRATION DE L'ALGORITHME D'HÉRITAGE AVEC EXCEPTIONS ===")
        
        # Test 1: Propriétés héritées d'un oiseau
        print("\n1. Propriétés héritées d'un oiseau:")
        oiseau_test = "Oiseau"
        resultat = algorithme_heritage_avec_exceptions(reseau, oiseau_test)
        if "erreur" in resultat:
            print(f"Erreur: {resultat['erreur']}")
        else:
            print(f"Propriétés héritées pour {resultat['noeud']}:")
            for relation, valeurs in resultat['proprietes'].items():
                print(f"  {relation}: {', '.join(valeurs)}")
        
        # Test 2: Propriétés héritées d'un moineau (héritage normal)
        print("\n2. Propriétés héritées d'un moineau (héritage normal):")
        moineau_test = "Moineau"
        resultat = algorithme_heritage_avec_exceptions(reseau, moineau_test)
        if "erreur" in resultat:
            print(f"Erreur: {resultat['erreur']}")
        else:
            print(f"Propriétés héritées pour {resultat['noeud']}:")
            for relation, valeurs in resultat['proprietes'].items():
                print(f"  {relation}: {', '.join(valeurs)}")
        
        # Test 3: Propriétés héritées d'un pingouin (avec exception)
        print("\n3. Propriétés héritées d'un pingouin (avec exception):")
        pingouin_test = "Pingouin"
        resultat = algorithme_heritage_avec_exceptions(reseau, pingouin_test)
        if "erreur" in resultat:
            print(f"Erreur: {resultat['erreur']}")
        else:
            print(f"Propriétés héritées pour {resultat['noeud']}:")
            if not resultat['proprietes']:
                print("  Aucune propriété héritée à cause des exceptions")
            else:
                for relation, valeurs in resultat['proprietes'].items():
                    print(f"  {relation}: {', '.join(valeurs)}")
        
        # Test 4: Propriétés héritées pour tous les animaux
        print("\n4. Propriétés héritées pour tous les animaux:")
        resultats_tous = algorithme_heritage_avec_exceptions(reseau)
        for animal, proprietes in resultats_tous.items():
            # Filtrer pour n'afficher que les nœuds d'animaux (pas les actions)
            if animal in ["Animal", "Oiseau", "Mammifère", "Pingouin", "Moineau", "Chien"]:
                print(f"\nPropriétés de {animal}:")
                if not proprietes:
                    print("  Aucune propriété héritée")
                else:
                    for relation, valeurs in proprietes.items():
                        print(f"  {relation}: {', '.join(valeurs)}")
        
        # Test 5: Saturation du réseau
        print("\n5. Saturation du réseau:")
        reseau_sature = algorithme_heritage_avec_exceptions(reseau, saturer_reseau=True)
        
        print("Nombre d'arcs dans le réseau original:", len(reseau["edges"]))
        print("Nombre d'arcs dans le réseau saturé:", len(reseau_sature["edges"]))
        arcs_inferes = [arc for arc in reseau_sature["edges"] if "inferred" in arc and arc["inferred"]]
        print("Nombre d'arcs inférés:", len(arcs_inferes))
        
        # Liste des nouvelles relations inférées
        print("\nExemples de relations inférées:")
        for i, arc in enumerate(arcs_inferes[:5]):  # Afficher seulement les 5 premières pour la lisibilité
            de_label = obtenir_label(arc["from"], reseau["nodes"])
            vers_label = obtenir_label(arc["to"], reseau["nodes"])
            print(f"  {de_label} --({arc['label']})--> {vers_label}")
        
        # Visualiser le réseau saturé
        print("\nAffichage de la visualisation graphique du réseau saturé avec exceptions...")
        visualiser_reseau(reseau_sature)
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier 'reseau-exec.json' n'a pas été trouvé.")
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier JSON n'est pas correctement formaté.")
    except Exception as e:
        print(f"Erreur: {str(e)}")