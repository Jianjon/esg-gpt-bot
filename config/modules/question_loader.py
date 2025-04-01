import csv

def load_questions(filepath):
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)
