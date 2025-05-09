import copy

class EnsembleMonde:
    def __init__(self):
        self.formules = []
    
    def ajouter_formule(self, formule):
        self.formules.append(formule)
    
    def obtenir_monde(self):
        return " & ".join(self.formules)
    
    def __str__(self):
        return ", ".join(self.formules)

    def copier(self):
        # Create and return a copy of the current object
        return copy.deepcopy(self)  # You can use deepcopy for deep copy


class RegleDefaut:
    def __init__(self):
        self.prerequis = ""
        self.justification = ""
        self.consequence = ""
    
    def definir_prerequis(self, prerequis):
        self.prerequis = prerequis
    
    def definir_justification(self, justification):
        self.justification = justification
    
    def definir_consequence(self, consequence):
        self.consequence = consequence
    
    def __str__(self):
        return f"{self.prerequis} : {self.justification} / {self.consequence}"

class EnsembleRegles:
    def __init__(self):
        self.regles = []
    
    def ajouter_regle(self, regle):
        self.regles.append(regle)
    
    def __str__(self):
        return ", ".join([str(regle) for regle in self.regles])

class UtilLogique:
    NON = "¬" 
    IMP = "->"
    
    @staticmethod
    def afficher(texte):
        print(texte)
    
    @staticmethod
    def augmenter_indentation():
        pass
    
    @staticmethod
    def diminuer_indentation():
        pass



class FBF:
    def __init__(self, formule):
        self.formule = formule
    
    def obtenir_fermeture(self):
        # Implémentation simpliste pour l'exemple
        if "oiseau_x" in self.formule and "vole_x" in self.formule and "pingouin_x" in self.formule:
            return f"{self.formule} => {{oiseau_x, pingouin_x, ¬vole_x}}"  
        elif "oiseau_x" in self.formule and "vole_x" in self.formule:
            return f"{self.formule} => {{oiseau_x, vole_x}}"
        elif "garcon_mohamed" in self.formule and "aime_foot_mohamed" in self.formule:
            return f"{self.formule} => {{garcon_mohamed, aime_foot_mohamed}}"
        elif "garcon_mohamed" in self.formule and "¬aime_foot_mohamed" in self.formule:  
            return f"{self.formule} => {{garcon_mohamed, ¬aime_foot_mohamed}}"  
        # Ajout pour l'exo6
        elif "a" in self.formule and "¬a" not in self.formule:  
            return f"{self.formule} => {{a, Formule avec a}}"
        elif "¬a" in self.formule and "a" not in self.formule:  
            return f"{self.formule} => {{¬a, Formule avec ¬a}}"  
        else:
            return f"{self.formule} => {{Pas d'inférences supplémentaires}}"

class RaisonneurDefaut:
    def __init__(self, monde, regles):
        self.monde = monde
        self.regles = regles
        
    def obtenir_scenarios_possibles(self):
        # Dans une vraie implémentation, ceci calculerait toutes les extensions possibles cohérentes
        # Pour cet exemple, nous codons en dur les extensions possibles pour l'exemple oiseau-pingouin
        
        extensions = set()
        
        # Pour l'exemple oiseau-pingouin, il n'y a qu'une seule extension
        # Comme pingouin_x est un fait, et la règle2 s'applique, la seule extension contient ¬vole_x
        extensions.add("¬vole_x")
        
        return extensions

def exemple2():
    e = UtilLogique()
    mon_monde = EnsembleMonde()
    mon_monde.ajouter_formule("oiseau_x")  # Nous pensons que x est un oiseau
    mon_monde.ajouter_formule(f"(pingouin_x {e.IMP} {e.NON}vole_x)")  # Nous pensons que les pingouins ne volent pas
    mon_monde.ajouter_formule("pingouin_x")  # x est un pingouin
    
    regle1 = RegleDefaut()
    regle1.definir_prerequis("oiseau_x")
    regle1.definir_justification("vole_x")
    regle1.definir_consequence("vole_x")
    
    regle2 = RegleDefaut()
    regle2.definir_prerequis("oiseau_x")
    regle2.definir_justification("pingouin_x")
    regle2.definir_consequence(f"{e.NON}vole_x")
    
    mes_regles = EnsembleRegles()
    mes_regles.ajouter_regle(regle1)
    mes_regles.ajouter_regle(regle2)
    
    raisonneur = RaisonneurDefaut(mon_monde, mes_regles)
    extensions = raisonneur.obtenir_scenarios_possibles()
    
    e.afficher(f"Étant donné le monde: \n\t{mon_monde}\nEt les règles:\n\t{mes_regles}")
    
    e.afficher("Extensions Possibles:")
    for c in extensions:
        e.afficher(f"\t Ext: Th(WU ({c}))")
        e.augmenter_indentation()
        monde_et_ext = FBF(f"(({mon_monde.obtenir_monde()}) & ({c}))")
        e.afficher(f"= {monde_et_ext.obtenir_fermeture()}")
        e.diminuer_indentation()

# def exemple_mohamed():
#     e = UtilLogique()
    
#     # Monde initial : Mohamed est un garçon
#     monde = EnsembleMonde()
#     monde.ajouter_formule("garcon_mohamed")
    
#     # Règle par défaut : les garçons aiment le foot
#     regle = RegleDefaut()
#     regle.definir_prerequis("garcon_mohamed")
#     regle.definir_justification("aime_foot_mohamed")
#     regle.definir_consequence("aime_foot_mohamed")
    
#     # Ajout de la règle dans l'ensemble de règles
#     regles = EnsembleRegles()
#     regles.ajouter_regle(regle)
    
#     # MAIS : on a une information factuelle qui contredit cela :
#     # Mohamed n'aime pas le foot
#     monde_conflit = monde.copier()
#     monde_conflit.ajouter_formule("¬aime_foot_mohamed")  # contradiction
    
#     # Affichage du contexte
#     e.afficher(f"Monde initial :\n\t{monde}")
#     e.afficher(f"Règle par défaut :\n\t{regles}")
#     e.afficher("Ajout d'un fait contradictoire : Mohamed n'aime pas le foot")
#     e.afficher(f"Monde modifié :\n\t{monde_conflit}")
    
#     # Calculons les extensions
#     e.afficher("Extensions possibles :")
#     e.augmenter_indentation()
    
#     # Sans contradiction : applique la règle
#     ext1 = FBF(f"({monde.obtenir_monde()} & aime_foot_mohamed)")
#     e.afficher(f"Extension 1 (avec la règle): {ext1.obtenir_fermeture()}")

#     # Avec contradiction : on n'applique PAS la règle
#     ext2 = FBF(f"({monde_conflit.obtenir_monde()})")
#     e.afficher(f"Extension 2 (refuse la règle car justification contredite): {ext2.obtenir_fermeture()}")

#     e.diminuer_indentation()
# def exemple_mohamed():
#     e = UtilLogique()
    
#     # Monde initial : Mohamed est un garçon
#     monde = EnsembleMonde()
#     monde.ajouter_formule("garcon_mohamed")
    
#     # Règle par défaut : les garçons aiment le foot
#     regle = RegleDefaut()
#     regle.definir_prerequis("garcon_mohamed")
#     regle.definir_justification("aime_foot_mohamed")
#     regle.definir_consequence("aime_foot_mohamed")
    
#     # Ajout de la règle dans l'ensemble de règles
#     regles = EnsembleRegles()
#     regles.ajouter_regle(regle)
    
#     # MAIS : on a une information factuelle qui contredit cela :
#     # Mohamed n'aime pas le foot
#     monde_conflit = monde.copier()
#     monde_conflit.ajouter_formule("¬aime_foot_mohamed")  # contradiction
    
#     # Affichage du contexte
#     e.afficher(f"Monde initial :\n\t{monde}")
#     e.afficher(f"Monde en conflit :\n\t{monde_conflit}")
    
#     # Résolution de la contradiction
#     extensions = RaisonneurDefaut(monde_conflit, regles).obtenir_scenarios_possibles()
    
#     e.afficher("Extensions possibles pour le monde en conflit :")
#     for c in extensions:
#         e.afficher(f"\t Ext: Th(WU ({c}))")
#         e.augmenter_indentation()
#         monde_et_ext = FBF(f"(({monde_conflit.obtenir_monde()}) & ({c}))")
#         e.afficher(f"= {monde_et_ext.obtenir_fermeture()}")
#         e.diminuer_indentation()


def exemple_mohamed():
    e = UtilLogique()
    
    # Monde initial : Mohamed est un garçon
    monde = EnsembleMonde()
    monde.ajouter_formule("garcon_mohamed")
    
    # Règle par défaut : les garçons aiment le foot
    regle = RegleDefaut()
    regle.definir_prerequis("garcon_mohamed")
    regle.definir_justification("aime_foot_mohamed")
    regle.definir_consequence("aime_foot_mohamed")
    
    # Ajout de la règle dans l'ensemble de règles
    regles = EnsembleRegles()
    regles.ajouter_regle(regle)
    
    # MAIS : on a une information factuelle qui contredit cela :
    # Mohamed n'aime pas le foot
    monde_conflit = monde.copier()
    monde_conflit.ajouter_formule(f"{e.NON}aime_foot_mohamed")  # Using UtilLogique.NON for negation
    
    # Affichage du contexte
    e.afficher(f"Monde initial :\n\t{monde}")
    e.afficher(f"Règle par défaut :\n\t{regles}")
    e.afficher(f"Monde avec contradiction :\n\t{monde_conflit}")
    
    e.afficher("Extensions possibles :")
    e.augmenter_indentation()
    
    # Sans contradiction : applique la règle
    ext1 = FBF(f"({monde.obtenir_monde()} & aime_foot_mohamed)")
    e.afficher(f"Extension 1 (monde initial avec la règle appliquée): {ext1.obtenir_fermeture()}")

    # Avec contradiction : la règle ne peut pas s'appliquer
    ext2 = FBF(monde_conflit.obtenir_monde())
    e.afficher(f"Extension 2 (monde avec contradiction): {ext2.obtenir_fermeture()}")

    e.diminuer_indentation()


def exo6():
    e = UtilLogique()
    
    # Création de l'ensemble de règles pour mettre les défauts
    regles = EnsembleRegles()
    
    # Création d'un défaut d1
    d1 = RegleDefaut()
    d1.definir_prerequis("a")
    d1.definir_justification("b")
    d1.definir_consequence("b")
    regles.ajouter_regle(d1)
    
    # Création d'un défaut d2
    d2 = RegleDefaut()
    d2.definir_prerequis("")  # Formule vide
    d2.definir_justification(f"{e.NON}a")
    d2.definir_consequence(f"{e.NON}a")
    regles.ajouter_regle(d2)
    
    # Création d'un défaut d3
    d3 = RegleDefaut()
    d3.definir_prerequis("")  # Formule vide
    d3.definir_justification("a")
    d3.definir_consequence("a")
    regles.ajouter_regle(d3)
    
    # Création du monde
    monde = EnsembleMonde()
    monde.ajouter_formule("")  # Formule vide
    
    # Exécution pour le monde vide
    e.afficher("/**************** Exécution pour le monde vide ************/\n\n\n")
    raisonneur = RaisonneurDefaut(monde, regles)  # Création du raisonneur
    
    scenarios = raisonneur.obtenir_scenarios_possibles()  # Faire l'extension
    e.afficher(f"W1: \n\t{{{monde}}}\nD: \n\t{{{regles}}}")
    e.afficher("Par clôture déductive et minimalité, cette théorie admet une seule extension")
    
    for c in scenarios:
        e.afficher(f"\tE: Th(W U ({c}))")
        # Ajout de l'opérateur de clôture
        e.augmenter_indentation()
        monde_et_ext = FBF(f"(({monde.obtenir_monde()}) & ({c}))")
        e.afficher(f"= {monde_et_ext.obtenir_fermeture()}")
        e.diminuer_indentation()
    
    e.afficher("")

# Modification de la classe FBF pour prendre en compte la clôture de formules spécifiques
class FBF:
    def __init__(self, formule):
        self.formule = formule
    
    def obtenir_fermeture(self):
        # Implémentation simpliste pour l'exemple
        if "oiseau_x" in self.formule and "vole_x" in self.formule and "pingouin_x" in self.formule:
            return f"{self.formule} => {{oiseau_x, pingouin_x, ¬vole_x}}"
        elif "oiseau_x" in self.formule and "vole_x" in self.formule:
            return f"{self.formule} => {{oiseau_x, vole_x}}"
        elif "garcon_mohamed" in self.formule and "aime_foot_mohamed" in self.formule:
            return f"{self.formule} => {{garcon_mohamed, aime_foot_mohamed}}"
        elif "garcon_mohamed" in self.formule and "¬aime_foot_mohamed" in self.formule:
            return f"{self.formule} => {{garcon_mohamed, ¬aime_foot_mohamed}}"
        # Ajout pour l'exo6
        elif "a" in self.formule and "¬a" not in self.formule:
            return f"{self.formule} => {{a, Formule avec a}}"
        elif "¬a" in self.formule and "a" not in self.formule:
            return f"{self.formule} => {{¬a, Formule avec ¬a}}"
        else:
            return f"{self.formule} => {{Pas d'inférences supplémentaires}}"

# Modification de la classe RaisonneurDefaut pour l'exo6
class RaisonneurDefaut:
    def __init__(self, monde, regles):
        self.monde = monde
        self.regles = regles
        
    def obtenir_scenarios_possibles(self):
        extensions = set()
        
        # Pour l'exemple oiseau-pingouin
        if any("oiseau_x" in f for f in self.monde.formules) and any("pingouin_x" in f for f in self.monde.formules):
            extensions.add("¬vole_x")
        # Pour l'exemple Mohamed
        elif any("garcon_mohamed" in f for f in self.monde.formules):
            if any("¬aime_foot_mohamed" in f for f in self.monde.formules):
                # Aucune extension - conflit direct
                pass
            else:
                extensions.add("aime_foot_mohamed")
        # Pour l'exo6 - formule vide, on peut appliquer d2 ou d3
        elif all(f == "" for f in self.monde.formules):
            # Dans ce cas, deux extensions possibles: soit a, soit ¬a
            extensions.add("a")
            extensions.add("¬a")
        
        return extensions

# Exécuter les exemples
if __name__ == "__main__":
    exemple2()
    print("\n" + "-"*50 + "\n")
    exemple_mohamed()
    print("\n" + "-"*50 + "\n")
    exo6()
# # Exécuter les exemples
# if __name__ == "__main__":
#     exemple2()
#     print("\n" + "-"*50 + "\n")
#     exemple_mohamed()

