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


def algorithme_heritage(reseau, noeud_cible=None, saturer_reseau=False):
    """
    Algorithme d'héritage pour déduire les propriétés d'un nœud ou saturer le réseau.
    
    Args:
        reseau: Le réseau sémantique
        noeud_cible: Le nœud dont on veut déduire les propriétés (ou None pour saturer le réseau)
        saturer_reseau: Si True, sature le réseau en inférant toutes les relations possibles
    
    Returns:
        Un dictionnaire des propriétés héritées par nœud ou le réseau saturé
    """
    noeuds = reseau["nodes"]
    arcs = reseau["edges"]
    
    # Fonction pour trouver tous les parents d'un nœud (relations "is a")
    def trouver_parents(noeud_id):
        parents = []
        for arc in arcs:
            if arc["from"] == noeud_id and arc["label"] == "is a":
                parents.append(arc["to"])
        return parents
    
    # Fonction pour trouver toutes les propriétés directes d'un nœud
    def trouver_proprietes_directes(noeud_id):
        proprietes = {}
        for arc in arcs:
            if arc["from"] == noeud_id and arc["label"] != "is a":
                if arc["label"] not in proprietes:
                    proprietes[arc["label"]] = []
                proprietes[arc["label"]].append(arc["to"])
        return proprietes
    
    # Fonction récursive pour hériter des propriétés
    def heriter_proprietes(noeud_id, proprietes_heritees=None, visites=None):
        if proprietes_heritees is None:
            proprietes_heritees = {}
        if visites is None:
            visites = set()
            
        if noeud_id in visites:  # Éviter les cycles
            return proprietes_heritees
        
        visites.add(noeud_id)
        
        # Ajouter les propriétés directes
        proprietes_directes = trouver_proprietes_directes(noeud_id)
        for relation, valeurs in proprietes_directes.items():
            if relation not in proprietes_heritees:
                proprietes_heritees[relation] = []
            for valeur in valeurs:
                if valeur not in proprietes_heritees[relation]:
                    proprietes_heritees[relation].append(valeur)
        
        # Hériter des propriétés des parents
        parents = trouver_parents(noeud_id)
        for parent_id in parents:
            heriter_proprietes(parent_id, proprietes_heritees, visites)
            
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
    nom_fichier = "reseau.json"
    reseau = charger_reseau_syntaxique(nom_fichier)
    
    # Affiche la structure du réseau
    afficher_reseau(reseau)
    
    print("\n=== DÉMONSTRATION DES ALGORITHMES ===")
    
    print("\n1. Propagation de marqueurs avancée:")
    noeuds_source = ["Logique D ordre 1"]
    resultats = propagation_de_marqueurs_avancee(reseau, noeuds_source, relations_a_suivre=["is a", "part of"])
    for ligne in resultats:
        print(ligne)
    
    print("\n2. Algorithme d'héritage pour un nœud spécifique:")
    resultat = algorithme_heritage(reseau, "Logique D ordre 1")
    print(f"Propriétés héritées pour {resultat['noeud']}:")
    for relation, valeurs in resultat['proprietes'].items():
        print(f"  {relation}: {', '.join(valeurs)}")
    
    print("\n3. Propagation avec gestion des exceptions:")
    # Ajoutez une exception à votre réseau pour tester
    if not any(arc["label"] == "exception" for arc in reseau["edges"]):
        # Ajouter une exception pour tester
        logique_id = next(n["id"] for n in reseau["nodes"] if n["label"] == "Logique D ordre 1")
        systeme_id = next(n["id"] for n in reseau["nodes"] if n["label"] == "Systeme S5")
        reseau["edges"].append({
            "from": logique_id,
            "to": systeme_id,
            "label": "exception"
        })
    
    concepts1 = ["Logique D ordre 1"]
    concepts2 = ["Systeme S5"]
    resultats = propagation_avec_exceptions(reseau, concepts1, concepts2, "is a", ["is a", "part of"])
    for ligne in resultats:
        print(ligne)


# if __name__ == "__main__":
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