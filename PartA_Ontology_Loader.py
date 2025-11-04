# Part A 
'''
Load the ontology and prepare for graph parsing and MCQ generation
'''

from Utility_Files import load_ontology, get_label, summarize_ontology
ONTOLOGY_PATH = "/content/drive/MyDrive/OWL Files/cinema.owl"

USE_REASONER = False  # Toggle ON if reasoning is required

onto, owl_file = load_ontology(ONTOLOGY_PATH, USE_REASONER)  #Load Ontology
summarize_ontology(onto)   # Summarize Ontology

# Confirming readiness for next modules
print(f"Ontology file ready for RDF graph parsing: {owl_file}")