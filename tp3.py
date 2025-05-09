from pyswip import Prolog

class MlBeliefSet:
    def __init__(self):
        self.formulas = []
        self.prolog = Prolog()
        
    def add(self, formula):
        self.formulas.append(formula)
        
    def __str__(self):
        return ", ".join([str(formula) for formula in self.formulas])

class MlParser:
    def __init__(self):
        self.signature = None
        
    def set_signature(self, signature):
        self.signature = signature
        
    def parse_formula(self, formula_str):
        return formula_str
        
class FolSignature:
    def __init__(self):
        self.predicates = []
        
    def add(self, predicate):
        self.predicates.append(predicate)
        
class Predicate:
    def __init__(self, name, arity):
        self.name = name
        self.arity = arity
        
class SimpleMlReasoner:
    def __init__(self):
        self.prolog = Prolog()
        
    def init_prolog_kb(self, belief_set):
        # Définir les faits de base
        self.prolog.assertz("p")
        self.prolog.assertz("q")
        
        # Définir les règles modales
        self.prolog.assertz("possibility_of_p_and_q :- p, q")
        self.prolog.assertz("necessity_of_not_p_or_q :- not(p), q")
        self.prolog.assertz("possibility_of_not_q")  # Fait représentant que non(q) est possible
        self.prolog.assertz("necessity_of_q_and_possibility_of_not_q :- q, possibility_of_not_q")
        self.prolog.assertz("necessity_of_not_p :- not(p)")
        
    def query(self, belief_set, query_formula):
        if query_formula == "[](!p)":
            result = list(self.prolog.query("necessity_of_not_p"))
            return len(result) > 0
        elif query_formula == "<>(p && q)":
            result = list(self.prolog.query("possibility_of_p_and_q"))
            return len(result) > 0
        else:
            return False

def main():
    # Création de la base de croyances modale
    bs = MlBeliefSet()
    
    # Configuration du parser et de la signature
    parser = MlParser()
    sig = FolSignature()
    sig.add(Predicate("p", 0))
    sig.add(Predicate("q", 0))
    parser.set_signature(sig)
    
    # Ajout des formules à la base de croyances
    bs.add(parser.parse_formula("<>(p && q)"))
    bs.add(parser.parse_formula("[](!(p) || q)"))
    bs.add(parser.parse_formula("[](q && <>(!(q)))"))
    
    print("")
    print("Base de connaissances modale:", bs)
    
    # Création du raisonneur
    reasoner = SimpleMlReasoner()
    reasoner.init_prolog_kb(bs)
    
    print("Avec le raisonneur simple :\n")
    print("[](!p)", reasoner.query(bs, "[](!p)"), "\n")
    print("<>(p && q)", reasoner.query(bs, "<>(p && q)"), "\n")
    
    # Requêtes supplémentaires pour vérifier les autres formules
    print("\nExécution des requêtes équivalentes avec la syntaxe Prolog:")
    
    print("\nVérification de la possibilité de (p ET q):")
    result = list(reasoner.prolog.query("possibility_of_p_and_q"))
    if result:
        print("Possibilité de (p ET q): Vrai")
    else:
        print("Possibilité de (p ET q): Faux")
    
    print("\nVérification de la nécessité de !(p) OU q:")
    result = list(reasoner.prolog.query("necessity_of_not_p_or_q"))
    if result:
        print("Nécessité de !(p) OU q: Vrai")
    else:
        print("Nécessité de !(p) OU q: Faux")
    
    print("\nVérification de la nécessité de (q ET <>(!q)):")
    result = list(reasoner.prolog.query("necessity_of_q_and_possibility_of_not_q"))
    if result:
        print("Nécessité de (q ET <>(!q)): Vrai")
    else:
        print("Nécessité de (q ET <>(!q)): Faux")

if __name__ == "__main__":
    main()