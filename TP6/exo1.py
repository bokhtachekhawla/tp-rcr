from owlready2 import *

# Create the ontology
onto = get_ontology("http://example.org/knowledge.owl")

with onto:
    # Concepts (Classes)
    class MODE(Thing): pass
    class LMODE(MODE): pass
    class GMODE(MODE): pass
    class LCLASSIC(Thing): pass
    class LNONCLASSIC(Thing): pass
    class LOGIC(Thing): pass
    class SYNTAX(Thing): pass
    class SEMANTIC(Thing): pass
    class LANGUAGE(Thing): pass
    class ALPHABET(Thing): pass
    class RREECRITURE(Thing): pass
    class AXIOME(Thing): pass
    class RINFERENCE(Thing): pass
    class RVALUATION(Thing): pass
    class CONTRADICTIONS(Thing): pass

    # Roles (Object Properties)
    class compose(ObjectProperty):
        domain = [Thing]
        range = [Thing]
        
    class est_correcte(ObjectProperty):
        domain = [Thing]
        range = [Thing]
        
    class genere(ObjectProperty):
        domain = [Thing]
        range = [Thing]
        
    class definie(ObjectProperty):
        domain = [Thing]
        range = [Thing]
        
    class est_un(ObjectProperty):
        domain = [Thing]
        range = [Thing]

    # Define relationships between concepts
    SYNTAX.is_a.append(compose.min(2, RINFERENCE))
    SYNTAX.is_a.append(compose.min(3, AXIOME))
    AXIOME.is_a.append(est_correcte.some(Thing))
    SEMANTIC.is_a.append(compose.only(RVALUATION))
    LOGIC.is_a.append(definie.some(LANGUAGE))
    LOGIC.is_a.append(definie.some(SYNTAX))
    LOGIC.is_a.append(definie.some(SEMANTIC))
    LOGIC.is_a.append(Not(genere.some(CONTRADICTIONS)))

    # Logic system instances
    LMODAL_CLASS = LNONCLASSIC("LMODAL_CLASS")
    LDEFAUT = LNONCLASSIC("LDEFAUT")
    RBAYESIEN = GMODE("RBAYESIEN")
    RSEMANTIQUE = GMODE("RSEMANTIQUE")
    A4 = AXIOME("A4")
    LOGPRED = LCLASSIC("LOGPRED")
    LOGPRED.compose.append(A4)
    SYST_T = LNONCLASSIC("SYST_T")
    A7 = AXIOME("A7")
    SYST_T.compose.append(A7)

# Optionally, save the ontology
onto.save(file="exo1.owl", format="rdfxml")

# Running reasoner
sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)

# Test conclusions

# 1. Verify the classification of LOGPRED and SYST_T
print(f"LOGPRED is of type: {list(LOGPRED.is_a)}")
print(f"SYST_T is of type: {list(SYST_T.is_a)}")

# 2. Check if SYNTAX is composed of the required RINFERENCE and AXIOME
print(f"SYNTAX should be composed of at least 2 RINFERENCE and 3 AXIOME: {SYNTAX.compose[0]}")


# 3. Ensure that LOGIC does not generate contradictions
logic_no_contradictions = not any([logic.genere for logic in LOGIC.instances() if CONTRADICTIONS in logic.genere])
print(f"Does LOGIC generate contradictions? {'No' if logic_no_contradictions else 'Yes'}")
