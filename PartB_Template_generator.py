# @title json file creation
import json

question_templates = {
    "taxonomy_relations": [
        "What category does {child} belong to?",
        "{child} is classified as which type?",
        "Which of the following is the parent class of {child}?",
        "Under which category would you find {child}?"
    ],

    "role_relations": [
        "What is the {prop_text} of {subject}?",
        "Which entity serves as the {prop_text} for {subject}?",
        "In the context of {subject}, what is the {prop_text}?",
        "Identify the {prop_text} associated with {subject}."
    ],

    "relational_chains": [
        "Given that {x} is related to {y}, and {y} is related to {z}, what is the final entity connected to {x}?",
        "If {x} connects through {y}, which entity is ultimately linked?",
        "Through the connection {x} → {y} → ?, which final entity emerges?"
    ],

    "sibling_classes": [
        "Which of the following shares the same parent category as {entity1}?",
        "What is a peer entity of {entity1}?",
        "{entity1} and which other entity belong to the same category?"
    ],

    "data_property_facts": [
        "What is the {property} of {subject}?",
        "Identify the {property} value for {subject}.",
        "What value does {subject} have for {property}?"
    ],

    "director_questions": [
        "Who directed the movie {movie}?",
        "Which director was responsible for {movie}?",
        "Identify the director of {movie}.",
        "{movie} was directed by whom?"
    ],

    "actor_questions": [
        "Who starred in {movie}?",
        "Which actor appeared in {movie}?",
        "Name an actor from {movie}.",
        "Who was in the cast of {movie}?"
    ],

    "release_questions": [
        "When was {movie} released?",
        "What is the release year of {movie}?",
        "In which year did {movie} come out?",
        "Identify the release date of {movie}."
    ],

    "director_actor_chain": [
        "In {movie} directed by {director}, who was one of the main actors?",
        "Which actor appeared in {director}'s film {movie}?",
        "Name an actor from {movie}, a film by {director}."
    ]
}

with open("question_templates.json", "w", encoding="utf-8") as f:
    json.dump(question_templates, f, indent=2, ensure_ascii=False)

print("question_templates.json created successfully")
print(f"Total: {sum(len(v) for v in question_templates.values())} question templates are available")