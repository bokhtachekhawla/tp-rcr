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

def visualiser_reseau(reseau):
    """Visualise le réseau sémantique avec matplotlib et networkx"""
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

def propagation_de_marqueurs(reseau, liste_node1, liste_node2, relation_visee, relations_a_suivre=None):
    """
    Algorithme de propagation de marqueurs basique.
    
    Args:
        reseau: Le réseau sémantique
        liste_node1: Liste des nœuds source
        liste_node2: Liste des nœuds cible
        relation_visee: Relation à vérifier
        relations_a_suivre: Relations à suivre lors de la propagation
    
    Returns:
        Liste des résultats de propagation
    """
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
            
    return resultats

def propagation_de_marqueurs_avancee(reseau, noeuds_source, noeuds_cible=None, relation_visee=None, relations_a_suivre=None):
    """
    Version avancée de l'algorithme de propagation de marqueurs.
    
    Args:
        reseau: Le réseau sémantique
        noeuds_source: Liste des nœuds source marqués
        noeuds_cible: Liste des nœuds cible ou None pour trouver tous les nœuds atteignables
        relation_visee: Relation spécifique à vérifier ou None pour toutes relations
        relations_a_suivre: Relations à suivre lors de la propagation
    
    Returns:
        Liste de résultats contenant les chemins trouvés ou les nœuds atteignables
    """
    noeuds_reseau = reseau["nodes"]
    arcs = reseau["edges"]
    
    if relations_a_suivre is None:
        relations_a_suivre = ["is a"]  # Par défaut, suit uniquement les relations "is a"
    
    # Convertir les labels de nœuds en objets de nœuds
    sources = []
    for source in noeuds_source:
        noeud = next((n for n in noeuds_reseau if n["label"] == source), None)
        if noeud:
            sources.append(noeud)
    
    cibles = []
    if noeuds_cible:
        for cible in noeuds_cible:
            noeud = next((n for n in noeuds_reseau if n["label"] == cible), None)
            if noeud:
                cibles.append(noeud)
    
    resultats = []
    
    # Mode 1: Vérifier les chemins entre sources et cibles spécifiques
    if noeuds_cible:
        for source in sources:
            for cible in cibles:
                chemins = []
                pile = [{"from": source["id"], "chemin": [source["label"]], "relations": []}]
                visites = set()  # Utilisé pour éviter les cycles
                
                while pile:
                    courant = pile.pop()
                    courant_id = courant["from"]
                    chemin = courant["chemin"]
                    relations_chemin = courant["relations"]
                    
                    # Éviter les cycles
                    if courant_id in visites:
                        continue
                    visites.add(courant_id)
                    
                    # Vérifier si on a atteint la cible
                    if courant_id == cible["id"]:
                        if relation_visee is None or (relations_chemin and relations_chemin[-1] == relation_visee):
                            chemins.append({
                                "chemin": chemin,
                                "relations": relations_chemin
                            })
                            # On continue à chercher d'autres chemins
                    
                    # Propage en suivant les relations spécifiées
                    for arc in arcs:
                        if arc["from"] == courant_id and (arc["label"] in relations_a_suivre or relation_visee is None):
                            noeud_suivant = obtenir_label(arc["to"], noeuds_reseau)
                            pile.append({
                                "from": arc["to"],
                                "chemin": chemin + [noeud_suivant],
                                "relations": relations_chemin + [arc["label"]]
                            })
                
                if chemins:
                    for chemin_info in chemins:
                        relations_str = " → ".join([f"({rel})" for rel in chemin_info["relations"]])
                        resultats.append(f"[✔] {' → '.join(chemin_info['chemin'])} | Relations: {relations_str}")
                else:
                    resultats.append(f"[✖] Pas de chemin entre {source['label']} et {cible['label']}")
    
    # Mode 2: Trouver tous les nœuds atteignables depuis les sources
    else:
        for source in sources:
            nœuds_atteignables = set()
            pile = [{"from": source["id"], "chemin": [source["label"]], "relations": []}]
            visites = set()
            
            while pile:
                courant = pile.pop()
                courant_id = courant["from"]
                chemin = courant["chemin"]
                relations_chemin = courant["relations"]
                
                if courant_id in visites:
                    continue
                visites.add(courant_id)
                
                # Ajouter le nœud courant aux nœuds atteignables
                label_courant = obtenir_label(courant_id, noeuds_reseau)
                if label_courant != source["label"]:  # Ne pas inclure le nœud source lui-même
                    nœuds_atteignables.add(label_courant)
                
                # Propage en suivant les relations spécifiées
                for arc in arcs:
                    if arc["from"] == courant_id and arc["label"] in relations_a_suivre:
                        noeud_suivant = obtenir_label(arc["to"], noeuds_reseau)
                        pile.append({
                            "from": arc["to"], 
                            "chemin": chemin + [noeud_suivant],
                            "relations": relations_chemin + [arc["label"]]
                        })
            
            if nœuds_atteignables:
                resultats.append(f"[✔] Nœuds atteignables depuis {source['label']}: {', '.join(nœuds_atteignables)}")
            else:
                resultats.append(f"[✖] Aucun nœud atteignable depuis {source['label']}")
    
    return resultats

if __name__ == "__main__":
    print("=== ALGORITHME DE PROPAGATION DE MARQUEURS ===")
    
    try:
        nom_fichier = "reseau.json"
        reseau = charger_reseau_syntaxique(nom_fichier)
        
        # Afficher la structure du réseau
        afficher_reseau(reseau)
        
        print("\n=== DÉMONSTRATION DE PROPAGATION DE MARQUEURS ===")
        
        # Test 1: Propagation de marqueurs basique
        print("\n1. Propagation de marqueurs basique:")
        concepts1 = ["Logique D ordre 1", "Topologie"]
        concepts2 = ["Systeme S5", "Mathematiques"]
        relation = "is a"
        relations_a_suivre = ["is a", "part of"]
        resultats = propagation_de_marqueurs(reseau, concepts1, concepts2, relation, relations_a_suivre)
        for ligne in resultats:
            print(ligne)
        
        # Test 2: Propagation avancée (nœuds atteignables)
        print("\n2. Propagation avancée (nœuds atteignables):")
        noeuds_source = ["Logique D ordre 1"]
        resultats = propagation_de_marqueurs_avancee(reseau, noeuds_source, relations_a_suivre=["is a", "part of"])
        for ligne in resultats:
            print(ligne)
        
        # Test 3: Propagation avancée entre deux nœuds spécifiques
        print("\n3. Propagation avancée entre nœuds spécifiques:")
        resultats = propagation_de_marqueurs_avancee(reseau, ["Logique D ordre 1"], ["Logique Modale"], 
                                                    relations_a_suivre=["is a"])
        for ligne in resultats:
            print(ligne)
            
        # Visualiser le réseau
        print("\nAffichage de la visualisation graphique du réseau...")
        visualiser_reseau(reseau)
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier 'reseau.json' n'a pas été trouvé.")
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier JSON n'est pas correctement formaté.")
    except Exception as e:
        print(f"Erreur: {str(e)}")