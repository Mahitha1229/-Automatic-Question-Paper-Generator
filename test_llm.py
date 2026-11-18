from llm_classifier import classify_batch

qs = [
    {"id": 1, "text": "Define a stack."},
    {"id": 2, "text": "Compare quicksort and mergesort in terms of time complexity."},
    {"id": 3, "text": "Design a data structure to implement an LRU cache."},
    {"id": 4, "text": "Fill in the blank: A ____ follows the LIFO principle."},
    {"id": 5, "text": "Justify why a hash table is better than a BST for lookups."},
]
for k, v in classify_batch(qs).items():
    print(k, v)