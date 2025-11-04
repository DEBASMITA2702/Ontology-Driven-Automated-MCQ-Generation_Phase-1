# PartB.py
# RDF Graph Preparation for Template Generation
'''
Loads the ontology, parses it into rdflib.graph, binds a base namespace,
and detects a label-like property for readable naming in later parts.
'''

from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
from Utility_Files import get_label

# Ensure ontology file is available from previous PartA
if "owl_file" not in globals():
    raise RuntimeError("'owl_file' not found. Run PartA.py first to load ontology.")

print("Starting to parse the ontology...")
g = Graph()
g.parse(owl_file, format="xml")  # Parse ontology into RDF graph
print("Ontology parsed.")

# Detect base namespace
ontology_iris = list(g.subjects(RDF.type, OWL.Ontology))
if ontology_iris:
    base_iri = str(ontology_iris[0]) + "#"
else:
    ns_list = [str(ns) for _, ns in g.namespaces() if not ns.startswith("http://www.w3.org/")]
    base_iri = ns_list[0] if ns_list else "http://default.org/ontology#"

GEN = Namespace(base_iri)
g.bind("gen", GEN)

# detect most common literal property
literal_props = {
    p for _, p, o in g.triples((None, None, None))
    if isinstance(o, Literal) and isinstance(o.value, str)
}

if literal_props:
    # Counting usage frequency
    prop_counts = {p: sum(1 for _ in g.triples((None, p, None))) for p in literal_props}
    found_label = max(prop_counts, key=prop_counts.get)
else:
    found_label = RDFS.label

print("RDF graph and label property initialized.")