import os

from typing import List

from anvil import Blueprint, GitSource, Source, run


class Tensorflow(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "tensorflow"

    @classmethod
    def source(cls) -> Source:
        return GitSource(
            "https://github.com/tensorflow/tensorflow",
            branch="v2.8.0",
            depth=1
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["bazelisk"]

    def build(self) -> None:
        paths = self.paths
        working_directory = paths.current_package_directory
        bazelisk_bin_directory = (
            paths.of("bazelisk").current_package_build_directory / "bin"
        )

        environment = {
            "PATH": f"{bazelisk_bin_directory}:{os.environ['PATH']}",
            "HOME": os.environ["HOME"]
        }

        #
        # TODO: Installation requires a Python 3 executable named "python"
        # (not "python3") in path
        #

        run(
            ["./configure"],
            environment=environment,
            working_directory=working_directory
        )

        run(
            [
                "bazel",
                "build",
                "-c",
                "opt",
                "--verbose_failures",
                "//tensorflow:libtensorflow_cc.so"
            ],
            environment=environment,
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return False
