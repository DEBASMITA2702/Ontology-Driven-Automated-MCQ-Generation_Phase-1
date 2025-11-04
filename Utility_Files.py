# @title Utility File Creation
#%%writefile Utility_Files.py
# Below are the core imports
from owlready2 import get_ontology, sync_reasoner
from rdflib import Graph, Namespace, RDF, RDFS, OWL
import urllib.parse
import pandas as pd
import os

# 4 helper functions below
# Ontology Loader
def load_ontology(path: str, use_reasoner: bool = False):
    """
    Loads ontology and optionally performs reasoning.
    Returns (ontology_object, owl_file_path).
    """
    onto = get_ontology(path).load()
    print(f"Ontology loaded successfully: {path}")

    if use_reasoner:
        print("Running HermiT reasoner (this may take a while)...")
        with onto:
            sync_reasoner()
        onto.save(file="reasoned.owl", format="rdfxml")
        print("Reasoning complete. Saved as 'reasoned.owl'.")
        return onto, "reasoned.owl"
    else:
        return onto, path

# Label Extractor
def get_label(entity):
    """
    Returns a clean human-readable label or IRI fragment fallback.
    Handles entities from Owlready2 or rdflib.
    """
    if entity is None:
        return ""
    if hasattr(entity, "label"):
        try:
            if entity.label:
                return entity.label.first()
        except Exception:
            pass

    # rdflib.URIRef or generic entity fallback
    uri = str(entity)
    label = uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]
    return urllib.parse.unquote(label)

# Path Utilities
def ensure_dir(path):
    """Creates directory if it doesn’t exist."""
    os.makedirs(path, exist_ok=True)

#Debug / Info Printer
def summarize_ontology(onto):
    """Prints summary counts of classes, individuals, and properties."""
    try:
        cls = list(onto.classes())
        inds = list(onto.individuals())
        ops = list(onto.object_properties())
        print(f"Classes: {len(cls)}, Individuals: {len(inds)}, ObjectProperties: {len(ops)}")
    except Exception:
        print("Could not summarize ontology (check ontology object type).")