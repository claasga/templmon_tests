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
        self.log = log
        self.exercise = exercise
        self.monpoly_started_event = asyncio.Event()

    def __del__(self):
        pass

    def receive_log_entry(self, log_entry):
        personnel_list = list(log_entry.personnel.all())
        # print("Personnel List in main thread: ")
        # print(personnel_list)
        material_list = list(log_entry.materials.all())
        asyncio.run_coroutine_threadsafe(
            self._receive_log_entry(log_entry, personnel_list, material_list), self.loop
        )

    async def _receive_log_entry(self, log_entry, personnel_list, material_list):
        print(f"Received log entry: {log_entry}")
        await self.monpoly_started_event.wait()  # Wait until monpoly is ready
        print("Monpoly is ready")
        try:
            monpolified_log_entry = transform(log_entry, personnel_list, material_list)
        except Exception as e:
            raise e
        print(f"Monpolified log entry: {monpolified_log_entry}")
        if self.monpoly.stdin:
            try:
                encoded = monpolified_log_entry.encode()
                self.monpoly.stdin.write(encoded)
                await self.monpoly.stdin.drain()
            except Exception as e:
                raise e
        else:
            raise Exception("Monpoly is not running")
        print("Log entry sent")

    async def read_output(self, process):
        self.monpoly_started_event.set()
        while True:
            line = await process.stdout.readline()
            if not line:
                print("process terminated")
                break
            print(f"Received: {line.decode('utf-8')[:-1]}")

    async def _launch_monpoly(
        self, loop: asyncio.AbstractEventLoop, mfotl_path, sig_path, rewrite=True
    ):
        """Has to be launched in a separate thread"""
        self.monpoly = await asyncio.create_subprocess_exec(
            "monpoly",
            "-sig",
            sig_path,
            "-formula",
            mfotl_path,
            "-verbose",
            "" if rewrite else "-no_rw",
            env=os.environ.copy(),  # Ensure the environment variables are passed
            stdin=asyncio.subprocess.PIPE,  # Allow writing to stdin
            stdout=asyncio.subprocess.PIPE,  # Capture stdout
            stderr=asyncio.subprocess.PIPE,  # Optionally capture stderr
        )
        asyncio.create_task(self.read_output(self.monpoly))
        self.monpoly_started_event.set()  # Signal that monpoly is ready

    def start_log_rule(self):
        def launch_listener_loop(loop: asyncio.AbstractEventLoop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        if (not self.loop) or (not self.loop.is_running()):
            threading.Thread(target=launch_listener_loop, args=(self.loop,)).start()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        mfotl_path = os.path.join(base_dir, "personnel_check.mfotl")
        sig_path = os.path.join(base_dir, "kdps.sig")
        asyncio.run_coroutine_threadsafe(
            self._launch_monpoly(
                self.loop,
                mfotl_path,
                sig_path,
            ),
            self.loop,
        )
        self.log.subscribe_to_exercise(self.exercise, self, send_past_logs=True)

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
        # atexitstuff"""
