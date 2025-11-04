# Install the dependencies
!pip install -q owlready2 rdflib pandas
import os
import urllib.parse
from owlready2 import get_ontology, sync_reasoner
from rdflib import Graph, Namespace, RDF, RDFS, OWL
import pandas as pd
from google.colab import drive
drive.mount('/content/drive', force_remount=False)

print("Environment ready. Drive mounted and libraries installed.")