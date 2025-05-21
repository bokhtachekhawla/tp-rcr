from owlready2 import *

onto = get_ontology("http://example.org/onto.owl")

with onto:
    class Personne(Thing): pass
    class Etudiant(Personne): pass
    class Enseignant(Personne): pass

    class a_enseigne(ObjectProperty):
        domain = [Enseignant]
        range = [Etudiant]
    
    # Individu
    Ryma = Personne("Ryma")
    khawla = Etudiant("khawla")
    
    # Assertion
    .a_enseigne.append(abbes)

# Raisonnement
sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

print(f"Khellaf types: {list(khellaf.is_a)}")
