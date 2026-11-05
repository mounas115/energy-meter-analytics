import csv
from datetime import datetime
from collections import defaultdict
from fileinput import filename
import statistics
import sys

MAX_KWH = 25.0


def parse_reading(row):
    meter_id = row.get("meter_id", "").strip()

    if not meter_id:
        return None, "MISSING_ID"

    try:
        timestamp = datetime.fromisoformat(row["timestamp"])
    except (ValueError, KeyError):
        return None, "BAD_TIMESTAMP"

    try:
        kwh = float(row["kwh"])
    except (ValueError, TypeError):
        return None, "BAD_KWH"

    if kwh != kwh or kwh < 0 or kwh > MAX_KWH:
        return None, "KWH_OUT_OF_RANGE"

    return (meter_id, timestamp, kwh), None


def load_readings(rows):
    valid = []
    rejected = defaultdict(int)
    seen = set()

    for row in rows:
        reading, error = parse_reading(row)

        if error:
            rejected[error] += 1
            continue

        key = (reading[0], reading[1])

        if key in seen:
            rejected["DUPLICATE"] += 1
            continue

        seen.add(key)
        valid.append(reading)

    return valid, dict(rejected)


def aggregate_hourly(readings):
    totals = defaultdict(float)

    for meter, timestamp, kwh in readings:
        hour = timestamp.replace(
            minute=0, second=0, microsecond=0
        )
        totals[(meter, hour)] += kwh

    return {key: round(value, 3)
            for key, value in totals.items()}


def aggregate_daily(readings):
    totals = defaultdict(float)

    for meter, timestamp, kwh in readings:
        totals[(meter, timestamp.date())] += kwh

    return {key: round(value, 3)
            for key, value in totals.items()}


def flag_unusual(hourly):
    grouped = defaultdict(list)

    for (meter, hour), kwh in hourly.items():
        grouped[meter].append(kwh)

    unusual = []

    for meter, values in grouped.items():
        median = statistics.median(values)

        if median > 0:
            for (m, hour), kwh in hourly.items():
                if m == meter and kwh > 3 * median:
                    unusual.append((meter, hour, kwh))

    return unusual


def main():
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "sample_readings.csv"
    with open(filename, newline="") as file:
        rows = list(csv.DictReader(file))

    valid, rejected = load_readings(rows)

    hourly = aggregate_hourly(valid)
    daily = aggregate_daily(valid)

    print("Valid readings:", len(valid))
    print("Rejected readings:", rejected)

    print("\nHourly totals:")
    for key, value in sorted(hourly.items()):
        print(key, "=", value, "kWh")

    print("\nDaily totals:")
    for key, value in sorted(daily.items()):
        print(key, "=", value, "kWh")

    print("\nUnusual usage:")
    print(flag_unusual(hourly))


if __name__ == "__main__":
    main()