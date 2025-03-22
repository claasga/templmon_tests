import json
import csv
from collections import defaultdict

patient_to_file = {
    "329396": "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_10-11-47 (copy)/329396_latencies.json",
    "404086": "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_10-11-47 (copy)/404086_latencies.json",
    # "726382": "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_10-11-47 (copy)/726382_latencies.json",
}
patient_data = {
    key: json.load(open(value, "r")) for key, value in patient_to_file.items()
}

trainer_file = open(
    "/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_10-11-47 (copy)/trainer_latencies.json",
    "r",
)
trainer_data = json.load(trainer_file)
unsorted_joined_data = []
for patient, patient_data in patient_data.items():
    unsorted_joined_data += zip(
        [v1 for v1, _ in patient_data],
        [v2 for _, v2 in patient_data],
        trainer_data[patient],
    )
sorted_joined_data = sorted(unsorted_joined_data, key=lambda x: x[0])
data_per_template = defaultdict(list)
for p_finish_time, p_rtt, measurement in sorted_joined_data:
    for template, (t_ft, t_rtt, _, t_monpoly) in measurement.items():
        data_per_template[template].append((p_rtt, t_rtt, t_monpoly))
# load files
# write data per template to csv, the header should be rtt_patient, rtt_trainer, monpoly
for template, data in data_per_template.items():
    with open(
        f"/home/claas/Desktop/BA/TemplMon/Performance Testing/measurements_2025-03-19_10-11-47 (copy)/cleaned_data/{template}.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerow(["rtt_patient", "rtt_trainer", "monpoly"])
        writer.writerows(data)
