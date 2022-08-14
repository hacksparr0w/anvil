import os

from typing import List

from anvil import Blueprint, GitSource, run


class Mlip(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "mlip"

    @classmethod
    def source(cls) -> GitSource:
        return GitSource(
            "git@gitlab.com:ashapeev/mlip-2.git"
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return []

    def build(self) -> None:
        paths = self.paths
        build_directory = paths.current_package_build_directory
        working_directory = paths.current_package_directory
        environment = {"PATH": os.environ["PATH"]}

        run(
            ["./configure", "--enable-debug", f"--prefix={build_directory}"],
            environment=environment,
            working_directory=working_directory
        )

        run(
            ["make", "mlp"],
            environment=environment,
            working_directory=working_directory
        )

        run(
            ["make", "libinterface"],
            environment=environment,
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
