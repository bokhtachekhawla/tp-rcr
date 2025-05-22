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
    G = nx.DiGraph()
    
    for noeud in reseau["nodes"]:
        G.add_node(noeud["id"], label=noeud["label"])
    
    for arc in reseau["edges"]:
        G.add_edge(arc["from"], arc["to"], 
                  label=arc["label"], 
                  edge_type=arc.get("edge_type", "default"))
    
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42, k=0.9)
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700, alpha=0.8)
    labels_noeuds = {noeud_id: G.nodes[noeud_id]['label'] for noeud_id in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels_noeuds, font_size=10)
    
    edges_normal = []
    edges_exception = []
    for u, v in G.edges():
        edge_data = G.edges[u, v]
        if edge_data.get("edge_type") == "exception" or edge_data["label"] == "exception":
            edges_exception.append((u, v))
        else:
            edges_normal.append((u, v))
    
    nx.draw_networkx_edges(G, pos, edgelist=edges_normal, width=1.0, alpha=0.7, 
                           arrowsize=15, arrowstyle='->', edge_color='gray')
    nx.draw_networkx_edges(G, pos, edgelist=edges_exception, width=2.0, alpha=0.9, 
                           arrowsize=20, arrowstyle='->', edge_color='red')
    
    labels_arcs = {(u, v): G.edges[u, v]['label'] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels_arcs, font_size=8, font_color='red')
    
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='gray', lw=1, label='Relation normale'),
        Line2D([0], [0], color='red', lw=2, label='Exception')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.title("Réseau Sémantique avec Exceptions", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def propagation_avec_exceptions(reseau, noeuds_source, noeuds_cible, relation_visee, relations_a_suivre=None):
    """
    Algorithme de propagation qui tient compte des liens d'exception.
    """
    noeuds = reseau["nodes"]
    arcs = reseau["edges"]
    
    if relations_a_suivre is None:
        relations_a_suivre = ["est un"]

    resultats = []

    for i in range(min(len(noeuds_source), len(noeuds_cible))):
        M1 = next((n for n in noeuds if n["label"].lower() == noeuds_source[i].lower()), None)
        M2 = next((n for n in noeuds if n["label"].lower() == noeuds_cible[i].lower() or n["id"] == noeuds_cible[i]), None)

        if not M1 or not M2:
            resultats.append(f"[✖] {noeuds_source[i]} ou {noeuds_cible[i]} n'existe pas dans le réseau.")
            continue

        # Vérifier s'il y a une exception directe
        exception_directe = any(
            arc["from"] == M1["id"] and arc["to"] == M2["id"] and est_exception(arc)
            for arc in arcs
        )
        
        if exception_directe:
            resultats.append(f"[✖] Exception directe: {noeuds_source[i]} ne peut pas faire {noeuds_cible[i]} ({relation_visee})")
            continue
        
        pile = [{"from": M1["id"], "chemin": [M1["label"]]}]
        visites = set()
        trouve = False
        exceptions = []

        while pile and not trouve:
            courant = pile.pop()
            courant_id = courant["from"]
            chemin = courant["chemin"]

            if courant_id in visites:
                continue
            visites.add(courant_id)
            
            a_exception = any(
                arc["from"] == courant_id and arc["to"] == M2["id"] and est_exception(arc)
                for arc in arcs
            )
            
            if a_exception:
                noeud_courant = obtenir_label(courant_id, noeuds)
                exceptions.append(f"{noeud_courant} → {noeuds_cible[i]}")
                continue
            
            for arc in arcs:
                if arc["from"] == courant_id and arc["to"] == M2["id"] and arc["label"] == relation_visee:
                    exception_existe = False
                    
                    noeud_actuel_id = courant_id
                    while not exception_existe:
                        if any(a["from"] == noeud_actuel_id and a["to"] == M2["id"] and est_exception(a) for a in arcs):
                            exception_existe = True
                            break
                        
                        parents = [a["to"] for a in arcs if a["from"] == noeud_actuel_id and a["label"] == "est un"]
                        if not parents:
                            break
                        noeud_actuel_id = parents[0]
                    
                    if not exception_existe:
                        chemin_complet = chemin + [M2["label"]]
                        resultats.append(f"[✔] {' → '.join(chemin_complet)} ({relation_visee})")
                        trouve = True
                        break
            
            if trouve:
                break

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
    
    nom_fichier = "reseau-exe.json"  # Ton fichier JSON
    
    reseau = charger_reseau_syntaxique(nom_fichier)
    
    afficher_reseau(reseau)
    
    print("\n=== Visualisation du réseau avec exceptions ===")
    visualiser_reseau_avec_exceptions(reseau)
    
    print("\n=== Tests de propagation ===")
    # Test 1 : oiseau → peut voler (en général oui sauf exceptions)
    tests1 = propagation_avec_exceptions(
        reseau,
        noeuds_source=["oiseau"],
        noeuds_cible=["peut voler"],
        relation_visee="peut"
    )
    for t in tests1:
        print(t)
    
    # Test 2 : autruche → peut voler (autruche est une exception)
    tests2 = propagation_avec_exceptions(
        reseau,
        noeuds_source=["autruche"],
        noeuds_cible=["peut voler"],
        relation_visee="peut"
    )
    for t in tests2:
        print(t)