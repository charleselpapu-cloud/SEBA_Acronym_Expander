import csv

# ---------------- CONFIG ----------------

INPUT = "point_names.csv"
OUTPUT = "expanded_points.csv"


# ---------------- COMMON SEBA ACRONYMS ----------------

import ast

ACRONYM_FILE = "Known_Acronyms.txt"


with open(ACRONYM_FILE, encoding="utf-8") as f:
    ACRONYMS = ast.literal_eval(f.read())


# Sort longest keys first
KEYS = sorted(
    ACRONYMS.keys(),
    key=len,
    reverse=True
)

# Longest match first
KEYS = sorted(ACRONYMS.keys(), key=len, reverse=True)


def expand_name(name):

    result = []

    i = 0

    while i < len(name):

        matched = False

        for key in KEYS:

            if name.startswith(key, i):

                result.append(ACRONYMS[key])
                i += len(key)
                matched = True
                break

        if matched:
            continue

        # Equipment numbers
        if name[i].isdigit():

            number = ""

            while i < len(name) and name[i].isdigit():
                number += name[i]
                i += 1

            if result:
                result[-1] += " " + number
            else:
                result.append(number)

            continue

        # Preserve unknown CamelCase segments as bracketed text
        start = i
        i += 1

        while i < len(name):

            if name[i].isdigit():
                break

            if name[i].isupper():
                break

            i += 1

        token = name[start:i]

        if token:
            result.append(f"[{token}]")

    return " ".join(result)


# ---------------- LOAD INPUT ----------------

with open(INPUT, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

if "Expanded Name" not in rows[0]:
    for row in rows:
        row["Expanded Name"] = ""

# ---------------- PROCESS ----------------

for row in rows:

    expanded = expand_name(row["Point Name"])

    row["Expanded Name"] = expanded

# ---------------- SAVE MAIN OUTPUT ----------------

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Expanded points written to: {OUTPUT}")
