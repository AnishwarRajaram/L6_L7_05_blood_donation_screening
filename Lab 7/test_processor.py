from hypothesis import given, strategies as st
from processor import validate_blood_type, calculate_pulse_pressure, parse_donor_registry

blood_like = st.builds(
    lambda pre, antigen, sign, post: f"{pre}{antigen}{sign}{post}",
    st.sampled_from(["", " ", "\t", "\n"]),
    st.sampled_from(["A", "B", "AB", "O", "a", "ab", "", "C", "ABO", "0"]),
    st.sampled_from(["+", "-", "", "*", "++", " "]),
    st.sampled_from(["", " ", "\n"]),
)

number_text = st.one_of(
    st.integers(min_value=-1000, max_value=1000).map(str),
    st.floats(allow_nan=True, allow_infinity=True).map(str),
    st.sampled_from(["", " ", "0", "-0", "abc", "1e3", "nan", "inf", "12.5.1", "1_000", "١٢٠"]),
)

bp_like = st.builds(
    lambda a, sep, b: f"{a}{sep}{b}",
    number_text,
    st.sampled_from(["/", "//", "\\", "", " / ", "/0/"]),
    number_text,
)

registry_like = st.lists(
    st.one_of(number_text, st.text(max_size=8)), min_size=0, max_size=5
).map("|".join)


# Fuzz validate_blood_type with arbitrary text or None and require it never raises.
@given(st.text() | st.none())
def test_validate_blood_type_no_crash(s):
    try:
        result = validate_blood_type(s)
    except Exception as e:
        assert False, f"validate_blood_type crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


# Fuzz validate_blood_type with near-valid blood codes so malformed antigens and signs are hit often.
@given(blood_like)
def test_validate_blood_type_structured(s):
    try:
        result = validate_blood_type(s)
    except Exception as e:
        assert False, f"validate_blood_type crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)
    if result.endswith(("Positive", "Negative")):
        assert result.split(" ")[0] in {"A", "B", "AB", "O"}


# Fuzz calculate_pulse_pressure with arbitrary text or None and require it never raises.
@given(st.text() | st.none())
def test_calculate_pulse_pressure_safe(s):
    try:
        result = calculate_pulse_pressure(s)
    except Exception as e:
        assert False, f"calculate_pulse_pressure crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


# Fuzz calculate_pulse_pressure with 'a/b' shaped inputs to reach zero, negative and non-numeric readings.
@given(bp_like)
def test_calculate_pulse_pressure_structured(s):
    try:
        result = calculate_pulse_pressure(s)
    except Exception as e:
        assert False, f"calculate_pulse_pressure crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)
    if result.startswith("Diff:"):
        diff = int(result.split(",")[0].split(":")[1])
        assert diff > 0, f"non-physiological reading {s!r} accepted as {result!r}"


# Fuzz parse_donor_registry with arbitrary text or None and require it never raises.
@given(st.text() | st.none())
def test_parse_donor_registry_safe(s):
    try:
        result = parse_donor_registry(s)
    except Exception as e:
        assert False, f"parse_donor_registry crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


# Fuzz parse_donor_registry with pipe-joined tokens to reach missing fields, nan/inf and bad numbers.
@given(registry_like)
def test_parse_donor_registry_structured(s):
    try:
        result = parse_donor_registry(s)
    except Exception as e:
        assert False, f"parse_donor_registry crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)
    if result.endswith(": Eligible"):
        _, weight, hb = s.split("|")
        assert float(weight) >= 50.0 and float(hb) >= 12.5
