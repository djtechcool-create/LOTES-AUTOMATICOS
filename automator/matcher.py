import json
import os
from fuzzywuzzy import fuzz, process

MAPPING_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mapping.json")


def load_mapping():
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_mapping(mapping):
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def normalize(text):
    return " ".join(text.upper().strip().split())


def match_product(excel_name, dali_products, threshold=60):
    mapping = load_mapping()
    norm_excel = normalize(excel_name)

    if norm_excel in mapping:
        cached = mapping[norm_excel]
        for d in dali_products:
            if normalize(d) == normalize(cached):
                return d, 100, "cache"

    dali_list = list(dali_products)
    if not dali_list:
        return None, 0, "no_products"

    norm_dali = [normalize(d) for d in dali_list]

    best_score = 0
    best_match = None

    for i, nd in enumerate(norm_dali):
        score_sort = fuzz.token_sort_ratio(norm_excel, nd)
        score_set = fuzz.token_set_ratio(norm_excel, nd)
        score = max(score_sort, score_set)
        if score > best_score:
            best_score = score
            best_match = dali_list[i]

    if best_score >= threshold:
        mapping[norm_excel] = best_match
        save_mapping(mapping)
        return best_match, best_score, "fuzzy"
    else:
        return None, best_score, "low_score"


def find_reference_in_egresos(referencia, egresos):
    referencia_str = str(referencia).strip()
    for eg in egresos:
        hojaruta = str(eg.get("HOJARUTA", "")).strip()
        if hojaruta.endswith(referencia_str):
            return eg
    return None
