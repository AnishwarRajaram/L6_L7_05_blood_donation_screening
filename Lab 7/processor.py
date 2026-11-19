import math
import re

VALID_ANTIGENS = {"A", "B", "AB", "O"}
RH_MAP = {"+": "Positive", "-": "Negative"}
BP_PATTERN = re.compile(r"\s*(\d{1,3})\s*/\s*(\d{1,3})\s*", re.ASCII)
NUMBER_PATTERN = re.compile(r"\s*\d+(\.\d+)?\s*", re.ASCII)


# Standardize an ABO/Rh code like 'O+' or 'ab-' into 'O Positive', returning an error message for invalid input.
def validate_blood_type(blood_code):
    if not isinstance(blood_code, str):
        return "Invalid input: blood type must be a string"
    cleaned = blood_code.strip().upper()
    if len(cleaned) < 2:
        return "Invalid blood type: expected format like A+, O-, AB+"
    antigen, rh_char = cleaned[:-1].strip(), cleaned[-1]
    if antigen not in VALID_ANTIGENS:
        return "Invalid blood type: antigen must be A, B, AB or O"
    if rh_char not in RH_MAP:
        return "Invalid blood type: Rh factor must be + or -"
    return f"{antigen} {RH_MAP[rh_char]}"


# Compute pulse pressure and systolic/diastolic ratio from 'systolic/diastolic', rejecting malformed or implausible readings.
def calculate_pulse_pressure(bp_string):
    if not isinstance(bp_string, str):
        return "Invalid input: BP must be a string"
    match = BP_PATTERN.fullmatch(bp_string)
    if not match:
        return "Invalid BP: expected format like 120/80"
    systolic, diastolic = int(match.group(1)), int(match.group(2))
    if not (40 <= diastolic < systolic <= 300):
        return "Invalid BP: reading out of physiological range"
    pulse_diff = systolic - diastolic
    ratio = round(systolic / diastolic, 2)
    return f"Diff: {pulse_diff}, Ratio: {ratio}"


# Parse a non-negative decimal token into a finite float, or return None if it is not a plain number.
def _parse_number(token):
    if not NUMBER_PATTERN.fullmatch(token):
        return None
    value = float(token)
    return value if math.isfinite(value) else None


# Parse 'DonorID|WeightKg|Hemoglobin' and report eligibility, returning an error message for malformed records.
def parse_donor_registry(donor_entry):
    if not isinstance(donor_entry, str):
        return "Invalid input: record must be a string"
    fields = donor_entry.split("|")
    if len(fields) != 3:
        return "Invalid record: expected ID|Weight|Hemoglobin"
    donor_id = fields[0].strip()
    if not donor_id or not donor_id.isprintable():
        return "Invalid record: donor ID must be non-empty printable text"
    weight = _parse_number(fields[1])
    hemoglobin = _parse_number(fields[2])
    if weight is None or hemoglobin is None:
        return "Invalid record: weight and hemoglobin must be numbers"
    if not (0 < weight <= 300) or not (0 < hemoglobin <= 25):
        return "Invalid record: weight or hemoglobin out of range"
    eligible = weight >= 50.0 and hemoglobin >= 12.5
    return f"Donor {donor_id}: {'Eligible' if eligible else 'Deferred'}"


# Read a line from the user, treating end-of-input as an empty string.
def _read(prompt):
    try:
        return input(prompt)
    except EOFError:
        return ""


# Prompt for one input per function and print each validated result.
def main():
    print("==== Running validate_blood_type ====")
    b_input = _read("Enter blood type (e.g. A+, O-, AB+): ")
    print("Validated:", validate_blood_type(b_input))

    print("\n==== Running calculate_pulse_pressure ====")
    bp_input = _read("Enter BP (e.g. 120/80): ")
    print("BP Metrics:", calculate_pulse_pressure(bp_input))

    print("\n==== Running parse_donor_registry ====")
    d_input = _read("Enter record (ID|Weight|Hemoglobin): ")
    print("Status:", parse_donor_registry(d_input))


if __name__ == "__main__":
    main()
