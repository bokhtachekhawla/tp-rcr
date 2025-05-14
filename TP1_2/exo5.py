from pyswip import Prolog

# Créer une instance Prolog
prolog = Prolog()

# Définir les faits et règles
prolog.assertz("livre(le_fils_du_pauvre)")
prolog.assertz("a_ecrit(mouloud_feraoun, le_fils_du_pauvre)")
prolog.assertz("auteur(Z) :- a_ecrit(Z, X), livre(X)")

# Poser la question
result = list(prolog.query("auteur(mouloud_feraoun)"))

# Afficher la réponse
print("Est-ce que Mouloud Feraoun est un auteur ?")
if result:
    print("Oui, Mouloud Feraoun est un auteur.")
else:
    print("Non, Mouloud Feraoun n’est pas un auteur.")
