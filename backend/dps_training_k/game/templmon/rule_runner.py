import os
import time
import asyncio
import threading
import subprocess
import logging
from collections import defaultdict

if __name__ != "__main__":
    from .output_parser import (
        DurationalViolationTracker,
        SingularViolationTracker,
        OutputParser,
    )
    from .rule_generators import ViolationType, LogRule
    from .log_transformer import MonpolyLogEntry
    from ..channel_notifications import ViolationDispatcher


class InvalidFormulaError(ValueError):
    pass


class RuleRunner:
    listening_loop = asyncio.new_event_loop()
    sessions = defaultdict(list)

    def __init__(
        self,
        session_id,
        log,
        log_rule: LogRule,
    ):
        self.valid = False
        self.log = log
        self.session_id = session_id
        self.log_rule = log_rule
        self.log_transformer = log_rule.log_transformer
        self.monpoly_started_event = asyncio.Event()
        self.finished_reading_monpoly = asyncio.Event()
        RuleRunner.sessions[self.session_id].append(self)
        self._lazy_pending_inputs = None
        self._initialized_stdin = False
        self._initialize_log_rule()
        self.output_read = None

    def __del__(self):
        pass

    @property
    def pending_inputs(self):
        if not self._lazy_pending_inputs:
            self._lazy_pending_inputs = asyncio.Queue()
        return self._lazy_pending_inputs

    @classmethod
    def start_session(cls, session_id):
        for log_rule_runner in cls.sessions[session_id]:
            log_rule_runner.start()

    @classmethod
    def stop_session(cls, session_id):
        for log_rule_runner in cls.sessions[session_id]:
            log_rule_runner.stop()

    def receive_log_entry(self, log_entry):
        transformed_log_entry = self.log_transformer.transform(log_entry)
        log_entry_type = self.log_transformer.determine_log_type(log_entry)
        # if log_entry_type == MonpolyLogEntry.UNKNOW_LOG_TYPE:
        #    return  # ToDo: remove
        # print(f"IN: Log Entry Type: {log_entry_type}")
        future = asyncio.run_coroutine_threadsafe(
            self._write_log_entry(transformed_log_entry, log_entry_type),
            self.listening_loop,
        )
        try:
            future.result()
        except Exception as e:
            print(f"Error in _write_log_entry: {e}")

    async def _send_and_process(self, input: str):
        input = f"{input}\n"
        encoded = input.encode()
        self.monpoly.stdin.write(encoded)
        await self.monpoly.stdin.drain()
        # print("RR: sending finished")

    async def _write_log_entry(
        self, monpolified_log_entry: str, log_type: MonpolyLogEntry
    ):
        await self.monpoly_started_event.wait()
        if (
            not self._initialized_stdin
        ):  # Race condition, ignored because we don't currently process things in parallel
            await self.pending_inputs.put(MonpolyLogEntry.COMMIT)
            await self._send_and_process(
                self.log_transformer.generate_commit(monpolified_log_entry)
            )
            self._initialized_stdin = True

        if self.monpoly.stdin:
            await self.pending_inputs.put((log_type, time.perf_counter()))
            print(
                f"RR: Queue size is now {self.pending_inputs.qsize()}, produced: {log_type}"
            )
            print(f"RR: Sending: {monpolified_log_entry}")
            self.output_read = asyncio.Event()
            await self._send_and_process(monpolified_log_entry)

            await self.output_read.wait()
            self.output_read = asyncio.Event()
            await self.pending_inputs.put((MonpolyLogEntry.COMMIT, None))
            print(
                f"RR: Queue size is now {self.pending_inputs.qsize()}, produced: {MonpolyLogEntry.COMMIT}"
            )
            print(
                f"RR: Sending: {self.log_transformer.generate_commit(monpolified_log_entry)}"
            )
            await self._send_and_process(
                self.log_transformer.generate_commit(monpolified_log_entry)
            )
            await self.output_read.wait()
            # print("*************************************")

            # print(
            #    f"IN: ({self.log_rule.template_name}, {self.log_rule.rule_name}): {monpolified_log_entry} of type {log_type}"
            # )
        else:
            raise Exception("Monpoly is not running")

    async def _launch_monpoly(self):
        """Has to be launched in a separate thread"""
        args = [
            "monpoly",
            "-sig",
            self.log_rule.signature,
            "-formula",
            self.log_rule.rule_file_path,
            "-verbose",
            "-nofilteremptytp",
        ]
        if not self.rewrite_allowed:
            args.append("-no_rw")
        self.monpoly = await asyncio.create_subprocess_exec(
            *args,
            env=os.environ.copy(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        tracker = (
            DurationalViolationTracker(
                self.free_variables,
                self.log_rule.same_violation_keys,
                ViolationDispatcher,
                self.session_id,
                self.log_rule.rule_name,
                self.log_rule.template_name,
            )
            if self.log_rule.violation_type.IS_DURATIONAL
            else SingularViolationTracker(
                self.free_variables,
                ViolationDispatcher,
                self.session_id,
                self.log_rule.rule_name,
                self.log_rule.template_name,
            )
        )
        out_p = OutputParser(self.monpoly, tracker, self)
        asyncio.create_task(out_p.read_output())
        self.monpoly_started_event.set()

    async def _terminate_monpoly(self):
        self.monpoly.stdin.close()
        await self.finished_reading_monpoly.wait()
        self.monpoly.terminate()

    def _extract_environment_variables(self, output: str):
        free_variables_predecessor = "The sequence of free variables is: ("
        start = output.find(free_variables_predecessor) + len(
            free_variables_predecessor
        )
        end = output.find(")", start)
        free_variables = output[start:end]
        free_variables = free_variables.split(",")
        return free_variables

    def _environment_infos(self):
        success_message = "formula is monitorable."
        terminated_process = subprocess.run(
            [
                "monpoly",
                "-sig",
                self.log_rule.signature,
                "-formula",
                self.log_rule.rule_file_path,
                "-check",
            ],
            capture_output=True,
            text=True,
        )
        print(terminated_process.stdout)
        if success_message in terminated_process.stdout:
            return (
                True,
                True,
                self._extract_environment_variables(terminated_process.stdout),
            )
        terminated_process = subprocess.run(
            [
                "monpoly",
                "-sig",
                self.log_rule.signature,
                "-formula",
                self.log_rule.rule_file_path,
                "-no_rw",
                "-check",
            ],
            capture_output=True,
            text=True,
        )
        print(terminated_process.stdout)
        if success_message in terminated_process.stdout:
            return (
                True,
                False,
                self._extract_environment_variables(terminated_process.stdout),
            )
        return False, None, None

    def _initialize_log_rule(self):
        self.valid, self.rewrite_allowed, self.free_variables = (
            self._environment_infos()
        )
        if not self.valid:
            raise InvalidFormulaError(f"Invalid formula: {self.log_rule.rule_name}")
        return self.free_variables

    def start(self):
        def launch_listener_loop(loop: asyncio.AbstractEventLoop):
            def handle_exception(loop, context):
                logging.error("Exception in event loop: %s", context)

            asyncio.set_event_loop(loop)
            loop.set_exception_handler(handle_exception)
            print("listener loop running")
            loop.run_forever()

        if (not self.listening_loop) or (not self.listening_loop.is_running()):
            threading.Thread(
                target=launch_listener_loop, args=(self.listening_loop,)
            ).start()

        if not self.valid:
            raise InvalidFormulaError("Invalid formula")
        asyncio.run_coroutine_threadsafe(
            self._launch_monpoly(),
            self.listening_loop,
        )
        self.log.subscribe_to_exercise(self.session_id, self, send_past_logs=True)

    def stop(self):
        asyncio.run_coroutine_threadsafe(self._terminate_monpoly(), self.listening_loop)
        self.log.unsubscribe_from_exercise(self.session_id, self)
