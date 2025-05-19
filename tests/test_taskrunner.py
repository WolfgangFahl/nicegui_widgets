"""
Created on 2025-05-18

@author: wf
"""

import asyncio
import time

from nicegui import Client, app, ui
from starlette.responses import JSONResponse

from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.ngwidgets_cmd import NiceguiWidgetsCmd
from ngwidgets.progress import TqdmProgressbar
from ngwidgets.task_runner import TaskRunner
from ngwidgets.version import Version
from ngwidgets.webserver import WebserverConfig
from ngwidgets.webserver_test import WebserverTest


class TaskSolution(InputWebSolution):
    """
    Task Solution class for testing TaskRunner via route.
    """

    def __init__(self, webserver: "TaskWebserver", client: Client):
        super().__init__(webserver, client)


class TaskWebserver(InputWebserver):
    """
    Minimal Webserver implementation for task testing.
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        config = WebserverConfig(
            short_name="tasktest",
            timeout=2.0,
            copy_right="(c)2025",
            version=Version(),
            default_port=8866,
        )
        config.solution_class = TaskSolution
        return config

    def __init__(self):
        super().__init__(config=self.get_config())

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


class TaskCmd(NiceguiWidgetsCmd):
    """
    Minimal Cmd class to comply with WebserverTest setup contract.
    """

    def __init__(self, config, server_class):
        super().__init__(config=config, webserver_cls=server_class)


class TestTaskRunner(WebserverTest):
    """
    Test the TaskRunner behavior inside a NiceGUI environment
    """

    def setUp(self, debug=True, profile=True):
        WebserverTest.setUp(
            self,
            server_class=TaskWebserver,
            cmd_class=TaskCmd,
            debug=debug,
            profile=profile,
        )

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
        self.assertEqual(result["async"], "done")
        self.assertEqual(result["blocking"], "done")
