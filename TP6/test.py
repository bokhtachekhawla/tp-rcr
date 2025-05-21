from owlready2 import *

onto = get_ontology("http://test.org/onto.owl")

with onto:
    class Person(Thing): pass
    class Food(Thing): pass
    class eats(Person >> Food): pass

    class Student(Person): pass
    class Pizza(Food): pass

    alice = Student("Alice")
    pizza = Pizza("Pizza")
    alice.eats = [pizza]

sync_reasoner_pellet(infer_property_values=True)

onto.save(file="test.owl", format="rdfxml")
