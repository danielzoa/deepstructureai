import platform
import psutil
import os


class SystemDiagnostics:

    def run(self):

        return {

            "python": platform.python_version(),

            "os": platform.system(),

            "cpu": platform.processor(),

            "memory_gb":
                round(
                    psutil.virtual_memory().total /
                    (1024 ** 3),
                    2
                ),

            "cwd": os.getcwd()
        }