# @title PartB_Templates.py

from rdflib import RDF, RDFS, OWL, Literal
from Utility_Files import get_label
import pandas as pd
import random

required_vars = ['g', 'GEN', 'found_label']
for v in required_vars:
    if v not in globals():
        raise RuntimeError(f"Missing variable '{v}'. Run PartB.py first.")

LIMITS = {
    "taxonomy": 200,
    "role": 200,
    "chain": 200,
    "sibling": 200,
    "data": 200,
    "directed": 150,
    "acted": 150,
    "released": 150
}

def safe_get_label(uri):
    """Wrapper around get_label() that handles rdflib entities safely."""
    try:
        return get_label(uri)
    except Exception:
        s = str(uri)
        return s.split("#")[-1] if "#" in s else s.split("/")[-1]

# TEMPLATE 1 – TAXONOMY RELATIONS
print("Extracting: Taxonomy relations (subClassOf)...")
q_taxonomy = """SELECT ?child ?parent WHERE { ?child rdfs:subClassOf ?parent . }"""
res_taxonomy = list(g.query(q_taxonomy))[:LIMITS["taxonomy"]]
df_taxonomy = pd.DataFrame(res_taxonomy, columns=["child", "parent"])
df_taxonomy["child_label"] = df_taxonomy["child"].apply(safe_get_label)
df_taxonomy["parent_label"] = df_taxonomy["parent"].apply(safe_get_label)
df_taxonomy.to_csv("taxonomy_relations.csv", index=False)
print("Saved taxonomy_relations.csv")

# TEMPLATE 2 – ROLE RELATIONS (Object Properties)
print("Extracting: Role relations (object properties)...")
obj_props = list(g.subjects(RDF.type, OWL.ObjectProperty))
rows = []
for p in obj_props:
    if len(rows) >= LIMITS["role"]:
        break
    for s, _, o in g.triples((None, p, None)):
        rows.append([p, s, o])
        if len(rows) >= LIMITS["role"]:
            break
df_roles = pd.DataFrame(rows, columns=["property", "subject", "object"])
df_roles["property_label"] = df_roles["property"].apply(safe_get_label)
df_roles["subject_label"] = df_roles["subject"].apply(safe_get_label)
df_roles["object_label"] = df_roles["object"].apply(safe_get_label)
df_roles.to_csv("role_relations.csv", index=False)
print("Saved role_relations.csv")

# TEMPLATE 3 – RELATIONAL CHAINS
print("Extracting: Relational chains...")
obj_props_sample = random.sample(obj_props, min(20, len(obj_props)))
chain_rows = []
for p1 in obj_props_sample:
    for p2 in obj_props_sample:
        if len(chain_rows) >= LIMITS["chain"]:
            break
        q = f"""
        SELECT ?x ?y ?z
        WHERE {{
            ?x <{p1}> ?y .
            ?y <{p2}> ?z .
        }}
        LIMIT 10
        """
        for x, y, z in g.query(q):
            chain_rows.append([p1, p2, x, y, z])
        if len(chain_rows) >= LIMITS["chain"]:
            break
df_chain = pd.DataFrame(chain_rows, columns=["prop1", "prop2", "x", "y", "z"])
for col in ["prop1", "prop2", "x", "y", "z"]:
    df_chain[f"{col}_label"] = df_chain[col].apply(safe_get_label)
df_chain.to_csv("relational_chains.csv", index=False)
print("Saved relational_chains.csv")

# TEMPLATE 4 – SIBLING CLASSES
print("Extracting: Sibling classes...")
q_siblings = """
SELECT ?e1 ?e2 ?parent
WHERE {
  ?e1 rdfs:subClassOf ?parent .
  ?e2 rdfs:subClassOf ?parent .
  FILTER(?e1 != ?e2)
}
"""
res_sib = list(g.query(q_siblings))[:LIMITS["sibling"]]
df_sib = pd.DataFrame(res_sib, columns=["entity1", "entity2", "parent"])
for col in ["entity1", "entity2", "parent"]:
    df_sib[f"{col}_label"] = df_sib[col].apply(safe_get_label)
df_sib.to_csv("sibling_classes.csv", index=False)
print("Saved sibling_classes.csv")

# TEMPLATE 5 – DATA PROPERTY FACTS
print("Extracting: Data property facts...")
data_props = list(g.subjects(RDF.type, OWL.DatatypeProperty))
data_rows = []
for p in data_props:
    if len(data_rows) >= LIMITS["data"]:
        break
    for s, _, o in g.triples((None, p, None)):
        if isinstance(o, Literal):
            data_rows.append([p, s, o])
        if len(data_rows) >= LIMITS["data"]:
            break
df_data = pd.DataFrame(data_rows, columns=["property", "subject", "value"])
df_data["property_label"] = df_data["property"].apply(safe_get_label)
df_data["subject_label"] = df_data["subject"].apply(safe_get_label)
df_data["value_str"] = df_data["value"].astype(str)
df_data.to_csv("data_property_facts.csv", index=False)
print("Saved data_property_facts.csv")

# TEMPLATE 6 – DIRECTOR QUESTIONS
director_props = [p for p in obj_props if 'director' in str(p).lower()]
director_rows = []
for p in director_props:
    for movie, _, director in g.triples((None, p, None)):
        director_rows.append([p, movie, director])
        if len(director_rows) >= LIMITS["directed"]:
            break
    if len(director_rows) >= LIMITS["directed"]:
        break

if director_rows:
    df_director = pd.DataFrame(director_rows, columns=["property", "movie", "director"])
    df_director["property_label"] = df_director["property"].apply(safe_get_label)
    df_director["movie_label"] = df_director["movie"].apply(safe_get_label)
    df_director["director_label"] = df_director["director"].apply(safe_get_label)
    df_director.to_csv("director_relations.csv", index=False)
    # print("Saved director_relations.csv")
# else:
    # print("No director relations found")

# TEMPLATE 7 – ACTOR QUESTIONS
actor_props = [p for p in obj_props if 'actor' in str(p).lower() or 'starring' in str(p).lower()]
actor_rows = []
for p in actor_props:
    for movie, _, actor in g.triples((None, p, None)):
        actor_rows.append([p, movie, actor])
        if len(actor_rows) >= LIMITS["acted"]:
            break
    if len(actor_rows) >= LIMITS["acted"]:
        break

if actor_rows:
    df_actor = pd.DataFrame(actor_rows, columns=["property", "movie", "actor"])
    df_actor["property_label"] = df_actor["property"].apply(safe_get_label)
    df_actor["movie_label"] = df_actor["movie"].apply(safe_get_label)
    df_actor["actor_label"] = df_actor["actor"].apply(safe_get_label)
    df_actor.to_csv("actor_relations.csv", index=False)
#     print("Saved actor_relations.csv")
# else:
#     print("No actor relations found")

# TEMPLATE 8 – DATE QUESTIONS
date_props = [p for p in data_props if any(kw in str(p).lower() for kw in ['date', 'year', 'release'])]
release_rows = []
for p in date_props:
    for movie, _, date_val in g.triples((None, p, None)):
        if isinstance(date_val, Literal):
            release_rows.append([p, movie, date_val])
        if len(release_rows) >= LIMITS["released"]:
            break
    if len(release_rows) >= LIMITS["released"]:
        break

if release_rows:
    df_release = pd.DataFrame(release_rows, columns=["property", "movie", "date"])
    df_release["property_label"] = df_release["property"].apply(safe_get_label)
    df_release["movie_label"] = df_release["movie"].apply(safe_get_label)
    df_release["date_str"] = df_release["date"].astype(str)
    df_release.to_csv("release_date_relations.csv", index=False)
#     print("Saved release_date_relations.csv")
# else:
#     print("No release date relations found")

print("\nAll template CSVs generated successfully.")