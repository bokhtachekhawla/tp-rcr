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
    """Déterminer si un arc représente une exception (vérifie edge_type et label)"""
    return arc.get("edge_type") == "exception" or arc["label"] == "exception"

def visualiser_reseau_avec_exceptions(reseau):
    """Visualise le réseau sémantique avec matplotlib et networkx en mettant en évidence les exceptions"""
    # Créer un graphe dirigé
    G = nx.DiGraph()
    
    # Ajouter les nœuds
    for noeud in reseau["nodes"]:
        G.add_node(noeud["id"], label=noeud["label"])
    
    # Ajouter les arêtes avec leurs labels et types
    for arc in reseau["edges"]:
        G.add_edge(arc["from"], arc["to"], 
                  label=arc["label"], 
                  edge_type=arc.get("edge_type", "default"))
    
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
    edges_normal = []
    edges_exception = []
    
    for u, v in G.edges():
        edge_data = G.edges[u, v]
        if edge_data.get("edge_type") == "exception" or edge_data["label"] == "exception":
            edges_exception.append((u, v))
        else:
            edges_normal.append((u, v))
    
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

def propagation_avec_exceptions(reseau, noeuds_source, noeuds_cible, relation_visee, relations_a_suivre=None):
    """
    Algorithme de propagation qui tient compte des liens d'exception.
    
    Args:
        reseau: Le réseau sémantique
        noeuds_source: Liste des nœuds source
        noeuds_cible: Liste des nœuds cible
        relation_visee: Relation à vérifier
        relations_a_suivre: Relations à suivre lors de la propagation
        
    Returns:
        Liste des résultats de propagation en tenant compte des exceptions
    """
# def propagation_avec_exceptions(reseau, noeuds_source, noeuds_cible, relation_visee, relations_a_suivre=None):
    noeuds = reseau["nodes"]
    arcs = reseau["edges"]
    
    if relations_a_suivre is None:
        relations_a_suivre = ["est un"]

    resultats = []

    for i in range(min(len(noeuds_source), len(noeuds_cible))):
        # Trouver le nœud source par son label
        # M1 = next((n for n in noeuds if n["label"] == noeuds_source[i]), None)
        
        # # Trouver le nœud cible par son label ou son ID
        # M2 = next((n for n in noeuds if n["label"] == noeuds_cible[i] or n["id"] == noeuds_cible[i]), None)
        # Trouver le nœud source par son label
        M1 = next((n for n in noeuds if n["label"] == noeuds_source[i]), None)

# Trouver le nœud cible par son label ou son ID
        M2 = next((n for n in noeuds if n["label"] == noeuds_cible[i] or n["id"] == noeuds_cible[i]), None)

        if not M1 or not M2:
            resultats.append(f"[✖] {noeuds_source[i]} ou {noeuds_cible[i]} n'existe pas dans le réseau.")
            continue
        
        # Le reste de la fonction reste inchangé...

        # Vérifier d'abord s'il existe une exception directe
        exception_directe = any(
            arc["from"] == M1["id"] and arc["to"] == M2["id"] and est_exception(arc)
            for arc in arcs
        )
        
        if exception_directe:
            resultats.append(f"[✖] Exception directe: {noeuds_source[i]} ne peut pas faire {noeuds_cible[i]} ({relation_visee})")
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
                arc["from"] == courant_id and arc["to"] == M2["id"] and est_exception(arc)
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
                        if any(a["from"] == noeud_actuel_id and a["to"] == M2["id"] and est_exception(a) for a in arcs):
                            exception_existe = True
                            break
                        
                        # Remonter aux parents s'il y en a
                        parents = [a["to"] for a in arcs if a["from"] == noeud_actuel_id and a["label"] == "est un"]
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
        nom_fichier = "reseau-ois-pin.json"
        reseau = charger_reseau_syntaxique(nom_fichier)
        
        # Afficher la structure du réseau
        afficher_reseau(reseau)
        
        # Afficher les exceptions existantes dans le réseau
        print("\n=== EXCEPTIONS DÉJÀ PRÉSENTES DANS LE RÉSEAU ===")
        exceptions_existantes = [arc for arc in reseau["edges"] if est_exception(arc)]
        for arc in exceptions_existantes:
            de_label = obtenir_label(arc["from"], reseau["nodes"])
            vers_label = obtenir_label(arc["to"], reseau["nodes"])
            print(f"  Exception: {de_label} → {vers_label} ({arc['label']})")
        
        print("\n=== DÉMONSTRATION DE PROPAGATION AVEC EXCEPTIONS ===")
        
        # Test: Vérifier la relation d'exception entre Pigeon et Oiseau
        print("\n1. Vérification de la relation d'exception entre Pigeon et Oiseau:")
        concepts1 = ["Pigeon"]
        concepts2 = ["Oiseau"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "ne vole pas", ["est un"])
        for ligne in resultats:
            print(ligne)
        
        # Visualiser le réseau avec les exceptions
        print("\nAffichage de la visualisation graphique du réseau avec exceptions...")
        visualiser_reseau_avec_exceptions(reseau)
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier JSON n'a pas été trouvé.")
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier JSON n'est pas correctement formaté.")
    except Exception as e:
        print(f"Erreur: {str(e)}")
# if __name__ == "__main__":
    print("=== ALGORITHME DE PROPAGATION AVEC EXCEPTIONS ===")
    
    try:
        nom_fichier = "reseau-exec.json"
        reseau = charger_reseau_syntaxique(nom_fichier)
        
        # Afficher la structure du réseau
        afficher_reseau(reseau)
        
        # Afficher les exceptions existantes dans le réseau
        print("\n=== EXCEPTIONS DÉJÀ PRÉSENTES DANS LE RÉSEAU ===")
        exceptions_existantes = [arc for arc in reseau["edges"] if est_exception(arc)]
        for arc in exceptions_existantes:
            de_label = obtenir_label(arc["from"], reseau["nodes"])
            vers_label = obtenir_label(arc["to"], reseau["nodes"])
            print(f"  Exception: {de_label} → {vers_label} ({arc['label']})")
        
        print("\n=== DÉMONSTRATION DE PROPAGATION AVEC EXCEPTIONS ===")
        
        # Test 1: Vérifier la capacité de vol des oiseaux (cas général)
        print("\n1. Vérification de la capacité de vol des oiseaux en général:")
        concepts1 = ["Oiseau"]
        concepts2 = ["vol"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "peut faire", ["est un"])
        for ligne in resultats:
            print(ligne)
        
        # Test 2: Vérifier la capacité de vol d'un moineau spécifique (héritage normal)
        print("\n2. Vérification de la capacité de vol d'un moineau:")
        concepts1 = ["Moineau"]
        concepts2 = ["vol"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "peut faire", ["est un"])
        for ligne in resultats:
            print(ligne)
        
        # Test 3: Vérifier la capacité de vol d'un pingouin (exception)
        print("\n3. Vérification de la capacité de vol d'un pingouin:")
        concepts1 = ["Pingouin"]
        concepts2 = ["vol"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "peut faire", ["est un"])
        for ligne in resultats:
            print(ligne)
            
        # Test 4: Vérifier la capacité de pondre des œufs pour le pingouin (héritage malgré l'exception sur le vol)
        print("\n4. Vérification de la capacité de pondre des œufs d'un pingouin:")
        concepts1 = ["Pingouin"]
        concepts2 = ["pond"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "peut faire", ["est un"])
        for ligne in resultats:
            print(ligne)
            
        # Test 5: Vérifier la capacité de marcher d'un mammifère
        print("\n5. Vérification de la capacité de marcher d'un mammifère:")
        concepts1 = ["Mammifère"]
        concepts2 = ["marche"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "peut faire", ["est un"])
        for ligne in resultats:
            print(ligne)
        
        # Test 6: Vérifier la capacité de marcher d'un chien (héritage de mammifère)
        print("\n6. Vérification de la capacité de marcher d'un chien:")
        concepts1 = ["Chien"]
        concepts2 = ["marche"]
        resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "peut faire", ["est un"])
        for ligne in resultats:
            print(ligne)
        
        # Visualiser le réseau avec les exceptions
        print("\nAffichage de la visualisation graphique du réseau avec exceptions...")
        visualiser_reseau_avec_exceptions(reseau)
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier 'reseau-exec.json' n'a pas été trouvé.")
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier JSON n'est pas correctement formaté.")
    except Exception as e:
        print(f"Erreur: {str(e)}")