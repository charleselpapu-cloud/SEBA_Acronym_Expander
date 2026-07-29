import csv
import requests
from difflib import get_close_matches


# ---------------- CONFIG ----------------

INPUT = "point_names.csv"
OUTPUT = "expanded_points.csv"
EXAMPLES = "SEBA_examples.txt"

URL = ""

# Use exact name from LM Studio /v1/models
MODEL = ""

BATCH = 20

# Number of similar SEBA examples to provide
SIMILAR_EXAMPLES = 10


# ----------------------------------------
# LOAD SEBA EXAMPLE DATABASE
# ----------------------------------------

def load_examples(filename):

    examples = []

    with open(
        filename,
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if "->" not in line:
                continue

            point, description = line.split(
                "->",
                1
            )

            point = point.strip()
            description = description.strip()

            if point and description:

                examples.append(
                    {
                        "point": point,
                        "description": description
                    }
                )

    return examples



examples = load_examples(EXAMPLES)


example_names = [
    x["point"]
    for x in examples
]


print(
    f"Loaded {len(examples)} SEBA examples"
)



# ----------------------------------------
# FIND SIMILAR SEBA POINTS
# ----------------------------------------

def get_similar_examples(points):

    selected = []


    for row in points:

        target = row["Point Name"]


        matches = []


        # Prefix matching
        for example in examples:

            name = example["point"]

            if (
                target.startswith(name)
                or name.startswith(target[:6])
            ):
                matches.append(example)



        # Similarity fallback
        if len(matches) < SIMILAR_EXAMPLES:

            similar = get_close_matches(
                target,
                example_names,
                n=SIMILAR_EXAMPLES,
                cutoff=0.25
            )

            for match in similar:

                for example in examples:

                    if example["point"] == match:
                        matches.append(example)
                        break



        # Longest / most informative first
        matches.sort(
            key=lambda x: len(x["point"]),
            reverse=True
        )


        for example in matches[:SIMILAR_EXAMPLES]:

            selected.append(
                f"{example['point']} -> {example['description']}"
            )


    return list(set(selected))



# ----------------------------------------
# BUILD PROMPT
# ----------------------------------------

def build_prompt(points):

    similar = get_similar_examples(points)


    example_text = "\n".join(similar)


    prompt = f"""
Role:
You are an expert in Schneider Electric SEBA point naming.

Goal:
Expand each unknown SEBA point name into its complete English description.

Constraints:
- Reply with ONLY one expanded point name per input line.
- Preserve the order of the inputs.
- Do not explain your reasoning.
- Do not include the original point name.
- Use natural readable English.
- If uncertain, make the most likely SEBA interpretation.
When an abbreviation has multiple possible meanings, prioritize:
1. Existing SEBA examples with the same surrounding abbreviations.
2. HVAC/BMS physical meaning.
3. Common Schneider Electric naming patterns.

Do not choose a meaning only because it is a common English abbreviation.

Context:
SEBA point names are constructed using abbreviated CamelCase naming.
The examples below are real SEBA naming examples.

Important:
- Use similar examples as patterns.
- Do not blindly copy examples.
- Infer missing words from the naming structure.
- Preserve equipment numbers.
- Use HVAC/BMS terminology.

Common Acronyms: 
Alm: Alarm
Spt: Setpoint
Sts: Status
Val: Value
Cmd: Command
Mode: Mode 
Tmp: Temperature
Fl: Flow
Pr: Pressure
Hum: Humidity
Pwr: Power
Pos: Position
Dmd: Demand
En: Enable
Ovr: Override
Rst: Reset
Spd: Speed
Vol: Volume
Occ: Occupancy
Eff: Effective
Dpr: Damper
Blr: Boiler
Htg: Heating
Cld: Cooling
Fan: Fan
Pmp: Pump
Vlv: Valve
Chlr: Chiller
Ct: Cooling Tower
Hex: Heat Exchanger
Econ: Economizer
Cmp: Compressor
Ahu: Air Handling Unit
Vav: Variable Air Volume
Ccu: Close Control Unit
Fcu: Fan Coil Unit
Ef: Exhaust Fan
Sf: Supply Fan
Rf: Return Fan
Oa: Outside Air
Sa: Supply Air
Ra: Return Air
Ea: Exhaust Air
Ma: Mixed Air
Znt: Zone Temperature
Rat: Return Air Temperature
Sat: Supply Air Temperature
Oat: Outside Air Temperature
Mat: Mixed Air Temperature
Chw: Chilled Water
Hw: Hot Water
Cw: Cold Water
Lwt: Leaving Water Temperature
Ewt: Entering Water Temperature
Vfd: Variable Frequency Drive
Iso: Isolation
Bps: Bypass
Loc: Local
Rem: Remote
Mnt: Maintenance
Flt: Fault
Run: Running
Sch: Schedule
Known SEBA Examples:

{example_text}

Point Names:

"""

    return prompt



# ----------------------------------------
# CALL MODEL
# ----------------------------------------

def ask(points):


    prompt = build_prompt(points)

    text = "\n".join(
        row["Point Name"]
        for row in points
    )


    payload = {

        "model": MODEL,

        "messages": [

            {
                "role": "system",
                "content": prompt
            },

            {
                "role": "user",
                "content": text
            }

        ],

        "temperature": 0.02,

        "max_tokens": 1500
    }


    response = requests.post(
        URL,
        json=payload
    )


    if response.status_code != 200:

        print("\nLM STUDIO ERROR:")
        print(response.text)

        exit()


    answer = response.json()["choices"][0]["message"]["content"]


    results = [

        line.strip()

        for line in answer.splitlines()

        if line.strip()

    ]


    while len(results) < len(points):

        results.append("")


    return results[:len(points)]



# ----------------------------------------
# LOAD INPUT CSV
# ----------------------------------------

with open(
    INPUT,
    encoding="utf-8"
) as f:

    rows = list(csv.DictReader(f))



if "Expanded Name" not in rows[0]:

    for row in rows:

        row["Expanded Name"] = ""



def save_rows():

    with open(
        OUTPUT,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)


    print("Progress saved")



def process_rows(rows_to_process, batch_size):

    todo = [
        row
        for row in rows_to_process
        if not row["Expanded Name"].strip()
    ]

    if not todo:
        return

    current_batch = todo[:batch_size]

    expansions = ask(current_batch)

    for row, expansion in zip(
        current_batch,
        expansions
    ):

        row["Expanded Name"] = expansion

    save_rows()

    incomplete = [
        row
        for row in current_batch
        if not row["Expanded Name"].strip()
    ]

    if incomplete and batch_size > 1:

        smaller_batch = max(1, batch_size // 2)

        print(
            f"Retrying {len(incomplete)} incomplete rows "
            f"with batch size {smaller_batch}"
        )

        process_rows(incomplete, smaller_batch)

    remaining = todo[batch_size:]

    if remaining:
        process_rows(remaining, batch_size)


# ----------------------------------------
# PROCESS BATCHES
# ----------------------------------------

for i in range(
    0,
    len(rows),
    BATCH
):

    batch = rows[i:i+BATCH]


    todo = [

        row

        for row in batch

        if not row["Expanded Name"].strip()

    ]


    if not todo:
        continue



    completed = sum(

        1

        for row in rows

        if row["Expanded Name"].strip()

    )


    print(
        f"\nRows {i+1}-{min(i+BATCH,len(rows))}"
        f" | {completed}/{len(rows)} completed"
    )



    process_rows(batch, BATCH)



print("\nDone.")
