import json
import csv
from collections import defaultdict

patient_to_file = {
    "128631": "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_09-21-05/128631_latencies.json",
    # "236406": "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_09-21-05/236406_latencies.json",
    "576418": "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_09-21-05/576418_latencies.json",
}
patient_data = {
    key: json.load(open(value, "r")) for key, value in patient_to_file.items()
}

unsorted_joined_data = []
for patient, patient_data in patient_data.items():
    for finish_time, rtt in patient_data:
        unsorted_joined_data.append((finish_time, rtt))
sorted_joined_data = [
    [tripping_time]
    for ft, tripping_time in sorted(unsorted_joined_data, key=lambda x: x[0])
]


with open(
    f"/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_09-21-05/cleaned_data/round_trip_times.csv",
    "w",
) as f:
    writer = csv.writer(f)
    writer.writerow(["rtt_patient"])
    writer.writerows(sorted_joined_data)
