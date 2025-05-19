"""
Created on 2025-05-18

@author: wf
"""

import asyncio
import time
import unittest

from ngwidgets.basetest import Basetest
from ngwidgets.task_runner import TaskRunner
from ngwidgets.test_live import LiveWebTest, LiveWebserver, LiveSolution, \
    LiveCmd
from nicegui import Client, ui
from starlette.responses import JSONResponse


class TaskSolution(LiveSolution):
    """
    Task Solution class for testing TaskRunner via route.
    """

    def __init__(self, webserver: "TaskWebserver", client: Client):
        super().__init__(webserver, client)


class TaskWebserver(LiveWebserver):
    """
    Minimal Webserver implementation for task testing.
    """

    def __init__(self):
        super().__init__()

        @ui.page("/taskrunner_async")
        async def taskrunner_async(client: Client):
            runner = TaskRunner(timeout=1)
            result = {}

            async def async_task():
                await asyncio.sleep(0.1)
                result["async"] = "done"

            runner.run_async(async_task)
            await asyncio.sleep(0.3)

            return JSONResponse(content=result)

        @ui.page("/taskrunner_blocking")
        async def taskrunner_blocking(client: Client):
            runner = TaskRunner(timeout=1)
            result = {}

            def blocking_task():
                time.sleep(0.1)
                result["blocking"] = "done"

            runner.run_blocking(blocking_task)
            await asyncio.sleep(0.2)

            return JSONResponse(content=result)

        @ui.page("/taskrunner_combined")
        async def taskrunner_combined(client: Client):
            runner = TaskRunner(timeout=1)
            result = {}

            async def async_task():
                await asyncio.sleep(0.1)
                result["async"] = "done"

            def blocking_task():
                time.sleep(0.1)
                result["blocking"] = "done"

            runner.run_async(async_task)
            runner.run_blocking(blocking_task)
            await asyncio.sleep(0.3)

            return JSONResponse(content=result)


class TaskCmd(LiveCmd):
    """
    Minimal Cmd class to comply with WebserverTest setup contract.
    """

    def __init__(self, config, server_class):
        super().__init__(config=config, webserver_cls=server_class)


class TestTaskRunnerLive(LiveWebTest):
    """
    Test the TaskRunner behavior using real HTTP requests
    """
    skip_tests = Basetest.inPublicCI()

    @classmethod
    def setUpClass(cls):
        if cls.skip_tests:
            cls.ws = None
        else:
            cls.ws = TaskWebserver()
            cls.ws.config.default_port = 8669
            cls.cmd = TaskCmd(cls.ws.config, TaskWebserver)
            cls.start_runner()

    def setUp(self, debug=True, profile=True):
        super().setUp(debug=debug, profile=profile)
        self.ws = TestTaskRunnerLive.ws

    @unittest.skipIf(skip_tests, "Skipped in public CI due to instability")
    def test_taskrunner_async(self):
        result = self.get_json("/taskrunner_async")
        self.assertEqual(result["async"], "done")

    @unittest.skipIf(skip_tests, "Skipped in public CI due to instability")
    def test_taskrunner_blocking(self):
        result = self.get_json("/taskrunner_blocking")
        self.assertEqual(result["blocking"], "done")

    @unittest.skipIf(skip_tests, "Skipped in public CI due to instability")
    def test_taskrunner_combined(self):
        result = self.get_json("/taskrunner_combined")
        self.assertEqual(result["blocking"], "done")
