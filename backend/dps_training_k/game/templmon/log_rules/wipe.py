import os

files = os.listdir("backend/dps_training_k/game/templmon/log_rules")
exclusions = ["wipe.py", "test_rule.mfotl"]
for file in files:
    if file not in exclusions:
        os.remove("backend/dps_training_k/game/templmon/log_rules/" + file)
