% Définition du domaine
ordinateur(a).

etudiant(b).
etudiant(c).

possede(b, a).

% Égalité (implémentée avec prédicat Prolog intégré (=)/2)
egale(X, Y) :- X = Y.
