import os
import time
import subprocess

initial_start = "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' up --build"
stop_containers = "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' down"
remove_volumes = "docker volume rm $(docker volume ls -qf dangling=true)"
start_containers = "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' up"

test_sizes = [2]
# test_sizes = [10, 20]
# test_sizes = [20]


class TestCases:
    PERSONNEL_CHECK = "pc"
    SYMPTOM_COMBINATION = "sc"
    PERSONNEL_PRIORITIZATION = "pp"
    TRIAGE_GOAL = "tg"
    FILTER = "ft"
    BERLIN = "bl"


template_configurations = [
    "",
    # ",".join(
    #     [
    #         TestCases.PERSONNEL_CHECK,
    #         TestCases.SYMPTOM_COMBINATION,
    #         TestCases.PERSONNEL_PRIORITIZATION,
    #         TestCases.TRIAGE_GOAL,
    #         TestCases.FILTER,
    #         TestCases.BERLIN,
    #     ]
    # ),
]
try:
    # Run initial "up --no-start"
    subprocess.run(
        "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' "
        "--env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' "
        "--project-name 'dps_training_k' up --no-start",
        shell=True,
        check=True,
    )
    # Start containers
    subprocess.run(
        "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' "
        "--env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' "
        "--project-name 'dps_training_k' start",
        shell=True,
        check=True,
    )
    # Wait for "Application startup complete" in logs
    subprocess.run(
        "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' "
        "--env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' "
        "--project-name 'dps_training_k' logs --follow --timestamps | grep -m 1 'Application startup complete'",
        shell=True,
        check=True,
    )

    for test_size in test_sizes:
        for template_configuration in template_configurations:
            with open("measurement_log.txt", "a") as log_file:
                log_file.write(
                    f"{time.localtime()}: Running test with {test_size} logs and templates {template_configuration}.\n”"
                )
            command_line_str = (
                f"python3 /home/claas/Desktop/BP/dps.training_k/performance_test/socket_connection_implicit.py "
                f"{test_size} {'--test_cases ' + template_configuration if template_configuration else ''}".strip()
            )
            # Run the test command
            result = subprocess.run(command_line_str, shell=True)
            if result.returncode != 0:
                with open("measurement_log.txt", "a") as log_file:
                    log_file.write(
                        f"{time.localtime()}:Test failed for test_size={test_size} and template_configuration='{template_configuration}.\n"
                    )
            else:
                with open("measurement_log.txt", "a") as log_file:
                    log_file.write(
                        f"{time.localtime()}: Fished test with {test_size} logs and templates {template_configuration}.\n”"
                    )
            # Stop containers
            subprocess.run(
                "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' "
                "--env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' "
                "--project-name 'dps_training_k' down",
                shell=True,
                check=True,
            )
            # Remove volumes
            subprocess.run(
                "docker volume rm $(docker volume ls -qf dangling=true)",
                shell=True,
                check=True,
            )
            # Start containers again
            subprocess.run(
                "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' "
                "--env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' "
                "--project-name 'dps_training_k' up",
                shell=True,
                check=True,
            )
            time.sleep(30)
            print("Test finished")
except Exception as e:
    print(e)
finally:
    subprocess.run(
        "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' "
        "--env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' "
        "--project-name 'dps_training_k' down",
        shell=True,
    )
    subprocess.run(
        "docker volume rm $(docker volume ls -qf dangling=true)",
        shell=True,
    )
