# @title PartC - MCQ Generation

import re, os, json, random, math, pandas as pd
from rdflib import RDFS
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

MCQ_LIMITS = {
    "taxonomy": 100,
    "role": 80,
    "chain": 60,
    "sibling": 80,
    "data": 80,
    "director": 100,
    "actor": 100,
    "release": 80,
    "director_actor": 60
}

#dependency check
if "g" not in globals() or "found_label" not in globals():
    raise RuntimeError("Please run PartB.py first to load the ontology graph 'g' and 'found_label'.")

# building label maps
uri_to_label, frag_to_label = {}, {}
for s in set(g.subjects()):
    s_str = str(s)
    frag = s_str.split("#")[-1] if "#" in s_str else s_str.rstrip("/").split("/")[-1]
    label_literal = None
    try:
        for lit in g.objects(s, found_label):
            label_literal = str(lit)
            break
    except Exception:
        pass
    if not label_literal:
        for lit in g.objects(s, RDFS.label):
            label_literal = str(lit)
            break
    if not label_literal:
        for _, o in g.predicate_objects(s):
            try:
                if isinstance(o, str) or (hasattr(o, "datatype") and o.datatype and "string" in str(o.datatype)):
                    label_literal = str(o)
                    break
            except Exception:
                continue
    uri_to_label[s_str] = label_literal or frag
    frag_to_label[frag] = label_literal or frag

#namespace filters
BAD_NAMESPACES = (
    "http://www.w3.org/",
    "https://www.w3.org/",
    "rdf-syntax-ns#",
    "rdf-schema#",
    "owl#",
    "xsd#",
)

def is_system_uri(s: str) -> bool:
    if not s:
        return True
    s = str(s)
    return any(ns in s for ns in BAD_NAMESPACES)

# helper function to clean ontology labels for natural text
def clean_label_text(label: str) -> str:
    """
    Cleans and normalizes ontology labels for natural language use. For example:
    - Removes punctuation and underscores.
    - Fixes camelCase and excessive capitalization.
    - Converts starting 'A' or 'An' to lowercase during mid-sentence.
    """
    if not label:
        return ""
    s = str(label).strip()
    # Replace underscores, hyphens with spaces
    s = re.sub(r"[_\-]+", " ", s)
    # Remove stray symbols but keep apostrophes and hyphens
    s = re.sub(r"[^\w\s'\-]", "", s)
    # Split camelCase (e.g. ComicBookHero -> Comic Book Hero)
    s = re.sub(r"(?<!^)(?=[A-Z])", " ", s)
    # Normalize spaces
    s = re.sub(r"\s+", " ", s).strip()
    # Lowercase first 'A' or 'An' if sentence fragment
    if re.match(r"^(A|An)\s+[A-Z]", s):
        s = s[0].lower() + s[1:]
    # Title-case only proper labels 
    words = s.split()
    if len(words) <= 3:
        s = s.title()
    else:
        # Capitalize first letter only for longer ones
        s = s[:1].lower() + s[1:] if s and s[0].isupper() else s
    return s.strip()


# label resolver
def resolve_label(val: str) -> str:
    if val is None:
        return ""
    val = str(val).strip()
    if is_system_uri(val):
        return ""
    if re.search(r"\w\s+\w", val):
        return val
    if val.startswith(("http://", "https://", "urn:")):
        candidate = uri_to_label.get(val, val.split("#")[-1] if "#" in val else val.split("/")[-1])
        return "" if is_system_uri(candidate) else candidate
    frag = val.split("#")[-1] if "#" in val else val.split("/")[-1]
    candidate = frag_to_label.get(frag, val)
    # return "" if is_system_uri(candidate) else candidate
    return "" if is_system_uri(candidate) else clean_label_text(candidate)

def clean(x):
    return str(x).strip() if pd.notna(x) else ""

def is_numeric(s):
    try:
        float(str(s))
        return True
    except:
        return False

def verbalize_property(p):
    """
    Convert property name to natural language.
    """
    if not p:
        return ""
    p = p.replace("_", " ").strip()

    # Remove common prefixes
    if p.startswith("has "):
        return p[4:].strip().lower()
    if p.startswith("is "):
        return p[3:].strip().lower()

    # Handling camelCase
    def camel_to_words(t):
        return re.sub(r"(?<!^)(?=[A-Z])", " ", t).lower()

    if p.startswith("has"):
        return camel_to_words(p[3:])
    if p.startswith("is"):
        return camel_to_words(p[2:])

    return camel_to_words(p).lower()

def pretty_prop(raw_val: str) -> str:
    """
    Clean, human-readable property phrase
    """
    s = clean(raw_val)
    candidate = resolve_label(s)

    if candidate.startswith(("http://","https://")) or s.startswith(("http://","https://")):
        src = s if s.startswith(("http://","https://")) else candidate
        candidate = src.split("#")[-1] if "#" in src else src.rstrip("/").split("/")[-1]

    # Remove technical terms
    candidate = re.sub(r"\bobject\s*property\b", "", candidate, flags=re.I)
    candidate = re.sub(r"\bdata\s*type\s*property\b", "", candidate, flags=re.I)
    candidate = re.sub(r"\bdatatype\s*property\b", "", candidate, flags=re.I)
    candidate = re.sub(r"\bowl\b", "", candidate, flags=re.I)
    candidate = re.sub(r"\bis\b", "", candidate, flags=re.I).strip()

    return verbalize_property(candidate)

# Loading CSVs
def read_csv_if_exists(f):
    return pd.read_csv(f) if os.path.exists(f) else pd.DataFrame()

frames = {
    "taxonomy": read_csv_if_exists("taxonomy_relations.csv"),
    "role": read_csv_if_exists("role_relations.csv"),
    "chain": read_csv_if_exists("relational_chains.csv"),
    "sibling": read_csv_if_exists("sibling_classes.csv"),
    "data": read_csv_if_exists("data_property_facts.csv"),
    "director": read_csv_if_exists("director_relations.csv"),
    "actor": read_csv_if_exists("actor_relations.csv"),
    "release": read_csv_if_exists("release_date_relations.csv"),
}

# Maintaining hierarchy for better distractors
parent_of, children_of = {}, {}
t = frames["taxonomy"]
if not t.empty:
    for _, row in t.iterrows():
        child = resolve_label(clean(row.get("child_label") or row.get("child")))
        parent = resolve_label(clean(row.get("parent_label") or row.get("parent")))
        if child and parent:
            parent_of.setdefault(child, set()).add(parent)
            children_of.setdefault(parent, set()).add(child)

def get_ancestors(lbl, max_hops=10):
    """Get all ancestors level by level."""
    visited = set()
    current_level = set(parent_of.get(lbl, set()))
    all_ancestors = []
    hops = 0

    while current_level and hops < max_hops:
        all_ancestors.append(list(current_level))
        visited |= current_level
        next_level = set()
        for p in current_level:
            next_level.update(parent_of.get(p, set()))
        current_level = next_level - visited
        hops += 1

    return all_ancestors

def hierarchical_sibling_distractors(lbl, k=3):
    """
    Generate distractors from siblings,
    then cousins,
    then higher levels.
    """
    lbl = clean(lbl)
    picks = []
    seen = {lbl}

    # Level 1: Direct siblings
    for p in parent_of.get(lbl, set()):
        sibs = [c for c in children_of.get(p, set()) if c not in seen and c != lbl]
        random.shuffle(sibs)
        for s in sibs:
            if len(picks) < k:
                picks.append(resolve_label(s))
                seen.add(s)
            else:
                return picks

    # Level 2+: higher level
    for level in get_ancestors(lbl, 10):
        candidates = []
        for anc in level:
            # Get siblings of this ancestor
            for grand_parent in parent_of.get(anc, set()):
                candidates += [c for c in children_of.get(grand_parent, set())
                             if c not in seen and c != anc]

        random.shuffle(candidates)
        for s in candidates:
            if len(picks) < k:
                picks.append(resolve_label(s))
                seen.add(s)
            else:
                return picks

    return picks[:k]

def numeric_distractors_from_pool(correct, pool, k=3):
    """
    Generate numeric distractors close to the correct value
    """
    try:
        c = float(correct)
    except:
        return []

    nums = []
    for v in pool:
        try:
            fv = float(v)
            if not math.isclose(fv, c):
                nums.append(fv)
        except:
            continue

    # Sort by distance from correct answer
    nums = sorted(set(nums), key=lambda x: abs(x - c))
    chosen = [str(int(x)) if float(x).is_integer() else str(x) for x in nums[:k]]

    # Add extra distractors
    for d in (1, 2, 3, 5, 10, 50, 100):
        if len(chosen) >= k:
            break
        for v in (c + d, c - d):
            if v > 0:  
                s = str(int(v)) if float(v).is_integer() else str(v)
                if s != str(correct) and s not in chosen:
                    chosen.append(s)
                    if len(chosen) == k:
                        break

    return chosen[:k]

# Templates & Distractors
with open("question_templates.json", "r", encoding="utf-8") as f:
    QUESTION_PATTERNS = json.load(f)

def pick_pattern(key):
    return random.choice(QUESTION_PATTERNS.get(key, ["{subject} – {property} – {object}"]))

def sanitize_distractors(options, answer):
    """Clean and validate distractors."""
    clean_opts = []
    for o in options:
        o = resolve_label(o)
        if not o or o == answer:
            continue
        if is_system_uri(o):
            continue
        if len(o) > 100:  # Skipping overly long labels
            continue
        if o not in clean_opts:
            clean_opts.append(o)
    return clean_opts[:3]

# Specialized distractor generators
def distractors_for_taxonomy(parent, k=3):
    return hierarchical_sibling_distractors(parent, k)

def distractors_for_sibling(e2, k=3):
    return hierarchical_sibling_distractors(e2, k)

def distractors_for_role_object(obj, prop, pool, k=3):
    """
    Generate distractors for role/object properties
    """
    # First hierarchical approach
    picks = hierarchical_sibling_distractors(obj, k)

    # Then add from pool if needed
    if len(picks) < k:
        vals = [x for x in pool if x and x != obj and x not in picks]
        random.shuffle(vals)
        picks += vals[:k - len(picks)]

    return picks[:k]

def distractors_for_chain(z, pool, k=3):
    """
    Generate distractors for chain questions
    """
    picks = hierarchical_sibling_distractors(z, k)

    if len(picks) < k:
        vals = [x for x in pool if x and x != z and x not in picks]
        random.shuffle(vals)
        picks += vals[:k - len(picks)]

    return picks[:k]

def distractors_for_data_value(val, prop, pool, k=3):
    """
    Generate distractors for data properties
    """
    v = str(val)

    # Numeric values
    if is_numeric(v):
        return numeric_distractors_from_pool(v, pool, k)

    # String values
    vals = [str(x).strip() for x in pool
            if str(x).strip() and str(x).strip() != v and not is_numeric(x)]
    random.shuffle(vals)
    return vals[:k]

# MCQ Generation
all_rows = []

def add_mcq(q, a, dist, src):
    all_rows.append([q, a, ", ".join(dist), src])

# TAXONOMY
df = frames["taxonomy"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["taxonomy"], len(df)), random_state=RANDOM_SEED)
    for _, r in df.iterrows():
        child = resolve_label(r.get("child_label") or r.get("child"))
        parent = resolve_label(r.get("parent_label") or r.get("parent"))
        if not (child and parent):
            continue

        q = pick_pattern("taxonomy_relations").format(child=child, parent=parent)
        d = sanitize_distractors(distractors_for_taxonomy(parent, 3), parent)
        if len(d) >= 2:  
            add_mcq(q, parent, d, "Taxonomy")

# ROLE
df = frames["role"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["role"], len(df)), random_state=RANDOM_SEED)
    pool = [resolve_label(x) for x in df.get("object", df.get("object_label", []))]

    for _, r in df.iterrows():
        subj = resolve_label(r.get("subject") or r.get("subject_label"))
        prop_raw = r.get("property") or r.get("property_label")
        obj = resolve_label(r.get("object") or r.get("object_label"))
        prop_text = pretty_prop(prop_raw)

        if not (subj and obj and prop_text):
            continue

        q = pick_pattern("role_relations").format(
            subject=subj, property=prop_text, prop_text=prop_text, object=obj
        )
        d = sanitize_distractors(distractors_for_role_object(obj, prop_text, pool, 3), obj)
        if len(d) >= 2:
            add_mcq(q, obj, d, "Role Relation")

# CHAIN 
df = frames["chain"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["chain"], len(df)), random_state=RANDOM_SEED)
    pool = [resolve_label(x) for x in df.get("z", df.get("z_label", []))]

    added = 0
    for _, r in df.iterrows():
        if added >= MCQ_LIMITS["chain"] // 2:
            break

        x = resolve_label(r.get("x") or r.get("x_label"))
        y = resolve_label(r.get("y") or r.get("y_label"))
        z = resolve_label(r.get("z") or r.get("z_label"))
        p1_text = pretty_prop(r.get("prop1") or r.get("prop1_label"))
        p2_text = pretty_prop(r.get("prop2") or r.get("prop2_label"))

        if not (x and y and z):
            continue

        q = pick_pattern("relational_chains").format(
            x=x, y=y, z=z, prop1=p1_text, prop2=p2_text,
            prop1_text=p1_text, prop2_text=p2_text
        )
        d = sanitize_distractors(distractors_for_chain(z, pool, 3), z)
        if len(d) >= 2:
            add_mcq(q, z, d, "Relational Chain")
            added += 1

# SIBLING
df = frames["sibling"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["sibling"], len(df)), random_state=RANDOM_SEED)
    for _, r in df.iterrows():
        e1 = resolve_label(r.get("entity1") or r.get("entity1_label"))
        e2 = resolve_label(r.get("entity2") or r.get("entity2_label"))
        p = resolve_label(r.get("parent") or r.get("parent_label"))

        if not (e1 and e2 and p):
            continue

        q = pick_pattern("sibling_classes").format(entity1=e1, entity2=e2, parent=p)
        d = sanitize_distractors(distractors_for_sibling(e2, 3), e2)
        if len(d) >= 2:
            add_mcq(q, e2, d, "Sibling Classes")

# DATA PROPERTY
df = frames["data"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["data"], len(df)), random_state=RANDOM_SEED)
    pools = df.groupby("property_label")["value_str"].apply(list).to_dict() if "property_label" in df.columns else {}

    for _, r in df.iterrows():
        subj = resolve_label(r.get("subject_label") or r.get("subject"))
        prop_raw = r.get("property_label") or r.get("property")
        val = clean(r.get("value_str") or r.get("value"))
        prop_text = pretty_prop(prop_raw)

        if not (subj and prop_text and val):
            continue

        q = pick_pattern("data_property_facts").format(subject=subj, property=prop_text)
        pool_vals = pools.get(r.get("property_label"), [])
        d = sanitize_distractors(distractors_for_data_value(val, prop_text, pool_vals, 3), val)
        if len(d) >= 2:
            add_mcq(q, val, d, "Data Property")

# DIRECTOR QUESTIONS
df = frames["director"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["director"], len(df)), random_state=RANDOM_SEED)
    all_directors = [resolve_label(x) for x in df.get("director", df.get("director_label", []))]

    for _, r in df.iterrows():
        movie = resolve_label(r.get("movie_label") or r.get("movie"))
        director = resolve_label(r.get("director_label") or r.get("director"))

        if not (movie and director):
            continue

        q = pick_pattern("director_questions").format(movie=movie)
        d = sanitize_distractors(distractors_for_role_object(director, "director", all_directors, 3), director)
        if len(d) >= 2:
            add_mcq(q, director, d, "Director Question")

# ACTOR QUESTIONS
df = frames["actor"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["actor"], len(df)), random_state=RANDOM_SEED)
    all_actors = [resolve_label(x) for x in df.get("actor", df.get("actor_label", []))]

    for _, r in df.iterrows():
        movie = resolve_label(r.get("movie_label") or r.get("movie"))
        actor = resolve_label(r.get("actor_label") or r.get("actor"))

        if not (movie and actor):
            continue

        q = pick_pattern("actor_questions").format(movie=movie)
        d = sanitize_distractors(distractors_for_role_object(actor, "actor", all_actors, 3), actor)
        if len(d) >= 2:
            add_mcq(q, actor, d, "Actor Question")

# RELEASE DATE QUESTIONS
df = frames["release"]
if not df.empty:
    df = df.sample(min(MCQ_LIMITS["release"], len(df)), random_state=RANDOM_SEED)
    all_dates = [clean(x) for x in df.get("date_str", [])]

    for _, r in df.iterrows():
        movie = resolve_label(r.get("movie_label") or r.get("movie"))
        date = clean(r.get("date_str") or r.get("date"))

        if not (movie and date):
            continue

        q = pick_pattern("release_questions").format(movie=movie)
        d = sanitize_distractors(distractors_for_data_value(date, "year", all_dates, 3), date)
        if len(d) >= 2:
            add_mcq(q, date, d, "Release Date")

# DIRECTOR-ACTOR CHAIN QUESTIONS
df_dir = frames["director"]
df_act = frames["actor"]
if not df_dir.empty and not df_act.empty:
    df_dir_clean = df_dir[["movie", "movie_label", "director", "director_label"]].copy()
    df_act_clean = df_act[["movie", "movie_label", "actor", "actor_label"]].copy()

    df_merged = pd.merge(df_dir_clean, df_act_clean, on=["movie", "movie_label"], how="inner")

    if not df_merged.empty:
        df_merged = df_merged.sample(min(MCQ_LIMITS["director_actor"], len(df_merged)), random_state=RANDOM_SEED)
        all_actors = [resolve_label(x) for x in df_act.get("actor", df_act.get("actor_label", []))]

        for _, r in df_merged.iterrows():
            movie = resolve_label(r.get("movie_label") or r.get("movie"))
            director = resolve_label(r.get("director_label") or r.get("director"))
            actor = resolve_label(r.get("actor_label") or r.get("actor"))

            if not (movie and director and actor):
                continue

            q = pick_pattern("director_actor_chain").format(movie=movie, director=director)
            d = sanitize_distractors(distractors_for_role_object(actor, "actor", all_actors, 3), actor)
            if len(d) >= 2:
                add_mcq(q, actor, d, "Director-Actor Chain")

# Save & Display
df_mcq = pd.DataFrame(all_rows, columns=["question", "correct_answer", "distractors", "source_template"])
df_mcq = df_mcq.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
df_mcq.to_csv("generated_mcqs.csv", index=False)
print(f"Generated {len(df_mcq)} MCQs")

# Global fallback entities for filler options
ALL_ENTITIES = [v for v in frag_to_label.values() if v and not is_system_uri(v)]

def display_formatted_mcq(row, idx):
    """Display MCQ in readable format."""
    q = row["question"].strip()
    corr = str(row["correct_answer"]).strip()
    dist = [d.strip() for d in str(row["distractors"]).split(",") if d.strip()]
    dist = sanitize_distractors(dist, corr)

    # Ensuring to have exactly 3 distractors
    while len(dist) < 3:
        filler = random.choice(ALL_ENTITIES)
        if filler != corr and filler not in dist:
            dist.append(filler)

    opts = dist[:3] + [corr]
    random.shuffle(opts)
    labels = ["A", "B", "C", "D"]
    ci = opts.index(corr)

    out = [f"\nQ{idx}. {q}"]
    for i in range(4):
        out.append(f"   {labels[i]}) {opts[i]}")
    out.append(f"\n   Answer: {labels[ci]}) {corr}")
    # out.append(f"   [Source: {row['source_template']}]")
    return "\n".join(out)

for i, row in df_mcq.head(15).iterrows():   # displaying 10 samples
    print(display_formatted_mcq(row, i+1))
    print("-"*80)

print(f"\n All Saved to: generated_mcqs.csv")