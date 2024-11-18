import subprocess
import asyncio
import os

tasks = []

# log = """@10 assigned_personnel(per_n_1, pat_n_1)
# @13 assigned_personnel(per_n_2, pat_n_1)
# @16 assigned_personnel(per_n_3, pat_n_1)
# @19 assigned_personnel(per_n_4, pat_n_1)
# @19.5 unknown_log_type(lalalalal)
# @20 assigned_personnel(per_n_5, pat_n_1)
# @21 unassigned_personnel(per_n_1)
# @22 unassigned_personnel(per_n_2)
# @30 assigned_personnel(per_n_1, pat_n_1)
# @31 assigned_personnel(per_n_2, pat_n_1)
# @32 unassigned_personnel(per_n_3)
# @33 assigned_personnel(per_n_3, pat_n_2)
# @35 assigned_personnel(per_n_6, pat_n_2)
# @37 assigned_personnel(per_n_7, pat_n_2)
# @39 assigned_personnel(per_n_8, pat_n_2)"""
log = """@70 assigned_personnel(hans, peter)
@71 assigned_personnel(hans, peter)
@72 assigned_personnel(hans, peter)
@73 assigned_personnel(hans, peter)
@74 assigned_personnel(hans, peter)
"""
# Get the absolute path of the current directory
base_dir = os.path.dirname(os.path.abspath(__file__))


async def read_output(process):
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        print(f"Received: {line.decode('utf-8')[:-1]}")


async def launch_task(*args):
    monpoly = await asyncio.create_subprocess_exec(
        *args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    tasks.append(monpoly)
    asyncio.create_task(read_output(monpoly))


async def send_input(subprocess, line):
    subprocess.stdin.write(line.encode())
    await subprocess.stdin.drain()


async def main():
    for i in range(500):
        await asyncio.create_task(
            launch_task(
                "monpoly",
                "-sig",
                os.path.join(base_dir, "kdps.sig"),
                "-formula",
                os.path.join(base_dir, "personnel_check copy.mfotl"),
                "-verbose",
            )
        )

    for line in log.split("\n"):
        for task in tasks:
            await send_input(task, line + "\n")
        await asyncio.sleep(1)  # might be turned off

        print(f"Sent: {line}")
    await asyncio.sleep(1)


asyncio.run(main())
