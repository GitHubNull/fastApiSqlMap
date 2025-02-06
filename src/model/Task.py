import tempfile
import os
import sys

from model.TaskStatus import TaskStatus
from third_lib.sqlmap.lib.core.datatype import AttribDict
from third_lib.sqlmap.lib.core.optiondict import optDict
from third_lib.sqlmap.lib.core.common import unArrayizeValue
from third_lib.sqlmap.lib.core.defaults import _defaults
from third_lib.sqlmap.lib.core.enums import MKSTEMP_PREFIX
from third_lib.sqlmap.lib.core.common import saveConfig
from third_lib.sqlmap.lib.core.subprocessng import Popen
from third_lib.sqlmap.lib.core.settings import IS_WIN
from third_lib.sqlmap.lib.core.data import logger


from model.Database import Database


class Task(object):
    def __init__(self, taskid, remote_addr, scanUrl, host, headers, body):
        self.status = TaskStatus.New
        self.start_datetime = None
        self.taskid = taskid
        self.scanUrl = scanUrl
        self.host = host
        self.headers = headers
        self.body = body
        self.remote_addr = remote_addr
        self.process = None
        self.output_directory = None
        self.options = None
        self._original_options = None
        self.initialize_options(taskid)

    def initialize_options(self, taskid):
        datatype = {"boolean": False, "string": None, "integer": None, "float": None}
        self.options = AttribDict()

        for _ in optDict:
            for name, type_ in optDict[_].items():
                type_ = unArrayizeValue(type_)
                self.options[name] = _defaults.get(name, datatype[type_])

        # Let sqlmap engine knows it is getting called by the API,
        # the task ID and the file path of the IPC database
        self.options.api = True
        self.options.taskid = taskid
        self.options.database = Database.filepath

        # Enforce batch mode and disable coloring and ETA
        self.options.batch = True
        self.options.disableColoring = True
        self.options.eta = False

        self._original_options = AttribDict(self.options)

    def set_option(self, option, value):
        self.options[option] = value

    def get_option(self, option):
        return self.options[option]

    def get_options(self):
        return self.options

    def reset_options(self):
        self.options = AttribDict(self._original_options)

    def engine_start(self):
        handle, configFile = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.CONFIG,
                                              text=True)
        os.close(handle)
        saveConfig(self.options, configFile)

        if os.path.exists("third_lib/sqlmap/sqlmap.py"):
            self.process = Popen([sys.executable or "python", "third_lib/sqlmap/sqlmap.py",
                                  "--api",
                                  "-c", configFile], shell=False,
                                 close_fds=not IS_WIN)
        elif os.path.exists(os.path.join(os.getcwd(), "sqlmap.py")):
            self.process = Popen([sys.executable or "python", "sqlmap.py",
                                  "--api", "-c", configFile], shell=False,
                                 cwd=os.getcwd(),
                                 close_fds=not IS_WIN)
        elif os.path.exists(os.path.join(os.path.abspath(os.path.dirname(
             sys.argv[0])), "sqlmap.py")):
            self.process = Popen([sys.executable or "python", "sqlmap.py",
                                  "--api", "-c", configFile], shell=False,
                                 cwd=os.path.join(
                                 os.path.abspath(os.path.dirname(sys.argv[0])))
                                 , close_fds=not IS_WIN)
        else:
            self.process = Popen(["sqlmap", "--api", "-c", configFile],
                                 shell=False, close_fds=not IS_WIN)

    def engine_stop(self):
        if self.process:
            self.process.terminate()
            return self.process.wait()
        else:
            return None

    def engine_process(self):
        return self.process

    def engine_kill(self):
        if self.process:
            try:
                self.process.kill()
                return self.process.wait()
            except Exception as e:
                logger.debug(e)
                return None
        return None

    def engine_get_id(self):
        if self.process:
            return self.process.pid
        else:
            return None

    def engine_get_returncode(self):
        if self.process:
            self.process.poll()
            return self.process.returncode
        else:
            return None

    def engine_has_terminated(self):
        return isinstance(self.engine_get_returncode(), int)
