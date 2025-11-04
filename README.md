# Ontology-Driven Automated MCQ Generation

This repository contains the complete implementation of an **Ontology-Driven Multiple Choice Question (MCQ) Generation System** — developed as part of a Master's thesis project.  
The project leverages **semantic web technologies**, **RDF reasoning**, and **template-based natural language generation** to automatically produce contextually meaningful MCQs from OWL ontologies.

---

## Project Overview

Traditional document-based question generation systems rely on unstructured text (PDFs or articles), which often lack semantic consistency.  
This project instead uses **ontologies** — structured, machine-interpretable knowledge graphs — as the foundation for question generation.

The system:
- Parses OWL ontologies (e.g., `cinema.owl`, `comicBook.owl`)
- Extracts semantic triples (subject–predicate–object)
- Maps relations to natural-language question templates
- Generates correct answers and plausible distractors
- Outputs questions in CSV and JSON formats

---

## Sequence of Execution

> All scripts must be executed sequentially in the following order.

| Step | File | Functionality |
|------|------|----------------|
| 1️⃣ | **`Environment_Setup.py`** | Handles all necessary imports, including `rdflib`, `pandas`, `owlready2`, and utility functions used across modules. Ensures compatibility and dependency consistency across all scripts. |
| 2️⃣ | **`Utility_Files.py`** | Defines helper functions for ontology loading, label extraction, path resolution, and debugging. Common utilities include `load_ontology()`, `get_label()`, and `summarize_ontology()`. These are reused in all subsequent scripts. |
| 3️⃣ | **`PartA_Ontology_Loader.py`** *(Ontology Initialization)* | Loads the target OWL ontology (e.g., `cinema.owl`) and initializes reasoning mode. Prepares the ontology for RDF graph parsing. The reasoner can be toggled via `USE_REASONER = True` for inferred triples. |
| 4️⃣ | **`PartB_Rdf_graph_builder.py`** *(RDF Graph Construction)* | Converts the loaded ontology into an RDF graph using `rdflib`. Dynamically detects namespaces, binds prefixes, and identifies label predicates. Saves RDF structure for downstream querying. |
| 5️⃣ | **`PartB_Relation_extractor.py`** *(Relation Extraction & Template Definition)* | Performs SPARQL queries to extract key relation types: taxonomy (subClassOf), object properties, data properties, sibling classes, and relational chains. Each relation type is then mapped to a corresponding linguistic template. |
| 6️⃣ | **`PartB_Template_generator.py`** *(Template Repository Construction)* | Generates a structured JSON file containing question templates. Each template includes parameterized linguistic patterns, e.g., `"Who is the {role} of {subject}?"` or `"Which of the following is a subclass of {parent_label}?"`. These templates make the system domain-independent. |
| 7️⃣ | **`PartC_MCQ_generator.py`** *(MCQ Generation and Output)* | The final stage. Combines extracted triples with templates to generate MCQs. Includes distractor generation (based on sibling entities), regex-based text cleaning, and export of results to CSV/JSON. |

---

## File Functionality Summary

### 1. `Import.py`
- Imports all Python libraries required across scripts.  
- Centralized to ensure consistent versioning across modules.  
- Includes a compatibility check for `Owlready2` and `rdflib` installations.

### 2. `Utility_Files.py`
- Core helper module.
- Functions:
  - `load_ontology(path, use_reasoner=False)` – loads and optionally reasons over the ontology.
  - `get_label(entity)` – retrieves human-readable names.
  - `summarize_ontology(onto)` – prints ontology metadata (classes, properties, individuals).
- These are called repeatedly in Parts A–C.

### 3. `PartA_Ontology_Loader.py`
- Entry point of the pipeline.  
- Loads OWL file and sets parameters:
  ```python
  ONTOLOGY_PATH = "/path/to/cinema.owl"
  USE_REASONER = False
- Calls utility functions to prepare ontology for RDF parsing.

### 4. `PartB_Rdf_Graph_Builder.py`
- Converts ontology to RDF triples using:
  ``` g.parse(owl_file, format="xml") ```
- Detects base namespaces dynamically.

- Identifies label properties (e.g., rdfs:label, hasName).
- Stores triples in CSV form for verification.

### 5. `PartB_Relation_Extractor.py`
- Performs SPARQL-based triple extraction for: Taxonomy (rdfs:subClassOf), Object Properties (owl:ObjectProperty), Data Properties, Sibling Class Relations, Relational Chains (multi-hop)
- Outputs categorized dataframes for each relation type.

### 6. `PartB_Template_Generator.py`
- Maps each relation type to one or more question templates.
- Stores all templates in a JSON file (question_templates.json).
- Supports language variation for naturalness.

### 7. `PartC_MCQ_Generator.py`

- Integrates all previous outputs to create final MCQs.
- Core steps:
    - Select appropriate template per triple.
    - Format question with correct labels.
    - Generate distractors (sibling or similar entities).
    - Clean text using regex normalization.

## Example Output (Cinema Ontology)

|  **Question** |  **Correct Answer** |  **Distractors** |
|-----------------|-----------------------|--------------------|
| Who directed the movie *The Shop Around the Corner*? | Ernst Lubitsch | Alfred Hitchcock, James Whale, Howard Hawks |
| Name an actor from *Horse Feathers*. | Chico Marx | Friedrich Feher, Lew Ayres, Nellie Bly Baker |
| Which of the following is a subclass of *Film*? | Silent Film | Talkie, Animated Film, Documentary |

**Final Output File:**
```bash
generated_mcqs.csv

