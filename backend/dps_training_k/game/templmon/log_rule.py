import os
import asyncio
import threading
from .log_transformer import transform


class LogRule:
    # There may be only one LogRule instance with the same values for each exercise
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SUB_DIR = "log_rules"  # ToDo
    RULE_FILENAME = "mfotl"
    DEFAULT_SIGNATURE = os.path.join(BASE_DIR, "kdps.sig")
    _count = -1

    def __init__(self, signature, templatefile, log_transformer):
        self.signature = signature
        self.templatefile = templatefile
        self.log_transformer = log_transformer

    # def __del__(self):
    #    os.remove(self.templatefile)

    @classmethod
    def create(cls, rule: str, name: str, log_transformer):
        file_path = os.path.join(
            cls.BASE_DIR, cls.SUB_DIR, cls._generate_temp_file_name(name)
        )
        with open(file_path, "w") as f:
            f.write(rule)
        return cls(cls.DEFAULT_SIGNATURE, file_path, log_transformer)

    @classmethod
    def _get_unique_number(cls):
        cls._count += 1
        return cls._count

    @classmethod
    def _generate_temp_file_name(cls, name):
        return f"{name}_{cls._get_unique_number()}.{cls.RULE_FILENAME}"


class LogRuleRunner:
    # I need to start monpoly before subscribing to the log or store the log entries
    loop = asyncio.new_event_loop()

    def __init__(self, exercise, log):
        print("init called with ", str(log))
        self.log = log
        self.exercise = exercise

    def __del__(self):
        pass

    async def receive_log_entry(self, log_entry):
        print("*******************************************")
        print("Received log entry: ", log_entry.pk)
        monpolified_log_entry = transform(log_entry)
        self.monpoly.stdin.write(monpolified_log_entry.encode())
        await self.monpoly.stdin.drain()

    async def read_output(self, process):
        self.monpoly_started_event.set()
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            print(f"Received: {line.decode('utf-8')[:-1]}")

    async def _launch_monpoly(
        self, loop: asyncio.AbstractEventLoop, mfotl_path, sig_path, rewrite=True
    ):
        """Has to be launched in a separate thread"""
        monpoly = await asyncio.create_subprocess_exec(
            "monpoly",
            "-sig",
            sig_path,
            "-formula",
            mfotl_path,
            "" if rewrite else "-no_rw",
            env=os.environ.copy(),  # Ensure the environment variables are passed
        )
        loop.call_soon_threadsafe(
            target=lambda: asyncio.create_task(self.read_output(monpoly))
        )
        await self.monpoly_started_event.wait()
        return monpoly

    def start_log_rule(self):
        print(
            "Current state of the loop: Is it running?" + str(self.loop.is_running())
            if self.loop
            else "No loop"
        )

        def launch_listener_loop(loop: asyncio.AbstractEventLoop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        self.monpoly_started_event = threading.Event()
        if (not self.loop) or (not self.loop.is_running()):
            threading.Thread(target=launch_listener_loop, args=(self.loop,)).start()
            print("started loop")
        print("Trying to run monpoly thread")
        self.monpoly = asyncio.run(
            self._launch_monpoly(
                self.loop,
                "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/personnel_check.mfotl",
                "/home/claas/Desktop/BP/dps.training_k/backend/dps_training_k/game/templmon/kdps.sig",
            )
        )
        print("Succeeded starting monpoly")
        self.log.subscribe_to_exercise(self.exercise, self, send_past_logs=True)
        print("Subscribed to exercise")

        # startup extra asyncio_thread as loop
        # asyncio.run(lauch_monpoly())
        # event.wait()
        # log.subscribe_to_exercise(exercise, self, send_past_logs=True)
        #
        # launch_monpoly()
        #   monpoly = await asyncio.create_subprocess_exec()
        #   listener_thread = loop.call_soon_threadsafe(asyncio.create_task, listener) oder eventuell
        #
        #
        #
        # atexitstuff
