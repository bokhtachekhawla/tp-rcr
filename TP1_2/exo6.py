from pyswip import Prolog

prolog = Prolog()
prolog.consult("facts.pl")

print("\nVérification des formules logiques :")

# Formule (a) : tous les ordinateurs ont exactement un propriétaire
print("\n[a] Tous les ordinateurs ont exactement un propriétaire :")
query_a = """
ordinateur(X),
findall(Y, possede(Y, X), Ys),
length(Ys, 1)
"""
result_a = list(prolog.query(query_a))
print("Satisfaite" if result_a else "Non satisfaite")

# Formule (b) : certains étudiants ont un ordinateur
print("\n[b] Certains étudiants ont un ordinateur :")
query_b = """
etudiant(X), ordinateur(Y), possede(X, Y)
"""
result_b = list(prolog.query(query_b))
print("Satisfaite" if result_b else "Non satisfaite")

# Formule (c) : certains étudiants n’ont pas d’ordinateur
print("\n[c] Certains étudiants n’ont pas d’ordinateur :")
query_c = """
etudiant(X), \\+ (ordinateur(Y), possede(X,Y))
"""
result_c = list(prolog.query(query_c))
print("Satisfaite" if result_c else "Non satisfaite")
