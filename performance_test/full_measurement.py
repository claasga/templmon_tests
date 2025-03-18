import os

initial_start = "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' up --build"
stop_containers = "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' down"
remove_volumes = "docker volume rm $(docker volume ls -qf dangling=true)"
start_containers = "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' up"

test_sizes = [2, 10, 30]


class TestCases:
    PERSONNEL_CHECK = "pc"
    SYMPTOM_COMBINATION = "sc"
    PERSONNEL_PRIORITIZATION = "pp"
    TRIAGE_GOAL = "tg"
    FILTER = "ft"
    BERLIN = "bl"


template_configurations = [
    "",
    TestCases.PERSONNEL_CHECK,
    TestCases.SYMPTOM_COMBINATION,
    TestCases.PERSONNEL_PRIORITIZATION,
    TestCases.TRIAGE_GOAL,
    TestCases.FILTER,
    TestCases.BERLIN,
    ",".join(
        [
            TestCases.PERSONNEL_CHECK,
            TestCases.SYMPTOM_COMBINATION,
            TestCases.PERSONNEL_PRIORITIZATION,
            TestCases.TRIAGE_GOAL,
            TestCases.FILTER,
            TestCases.BERLIN,
        ]
    ),
]
try:
    # os.system(initial_start)
    ## Wait for all containers to be built and finish their startup
    os.system(
        "docker compose --file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/docker-compose.yml' --env-file '/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/.env.dev' --project-name 'dps_training_k' logs --follow --timestamps | grep -m 1 'Application startup complete'"
    )
    for test_size in test_sizes:
        for template_configuration in template_configurations:
            print(
                f"Running test with {test_size} logs and templates {template_configuration}"
            )
            os.system(
                f"python3 /home/claas/Desktop/BP/dps.training_k/performance_test/socket_connection_implicit.py {test_size} {'--test_cases '+ template_configuration if template_configuration else ''}"
            )
            os.system(stop_containers)
            os.system(remove_volumes)
            os.system(start_containers)
            print("Test finished")
except Exception as e:
    print(e)
finally:
    os.system(stop_containers)
    os.system(remove_volumes)
