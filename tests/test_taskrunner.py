"""
Created on 2025-05-18

@author: wf
"""

import asyncio
import time

from ngwidgets.ngwidgets_cmd import NiceguiWidgetsCmd
from ngwidgets.task_runner import TaskRunner
from ngwidgets.version import Version
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui
from starlette.responses import JSONResponse

from ngwidgets.test_live import LiveWebTest, LiveServerRunner, LiveWebserver, LiveSolution, \
    LiveCmd


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

    @classmethod
    def setUpClass(cls):
        """Set up resources shared by all test methods"""
        # Create the task webserver
        cls.ws = TaskWebserver()

        # Create the cmd instance and get properly configured args
        cls.cmd = TaskCmd(cls.ws.config, TaskWebserver)
        cls.start_runner()

    def setUp(self, debug=True, profile=True):
        """Set up the test environment"""
        super().setUp(debug=debug, profile=profile)

    def test_taskrunner_async(self):
        """
        Test asynchronous task execution
        """
        result = self.get_json("/taskrunner_async")
        self.assertEqual(result["async"], "done")

    def test_taskrunner_blocking(self):
        """
        Test blocking task execution
        """
        result = self.get_json("/taskrunner_blocking")
        self.assertEqual(result["blocking"], "done")

    def test_taskrunner_combined(self):
        """
        Test combined async and blocking execution
        """
        result = self.get_json("/taskrunner_combined")
        #self.assertEqual(result["async"], "done")
        self.assertEqual(result["blocking"], "done")
