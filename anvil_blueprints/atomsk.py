import os

from typing import List

from anvil import Blueprint, GitSource, run


class Atomsk(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "atomsk"

    @classmethod
    def source(cls) -> GitSource:
        return GitSource("https://github.com/pierrehirel/atomsk.git")

    @classmethod
    def dependencies(cls) -> List[str]:
        return []

    def build(self) -> None:
        paths = self.paths
        build_directory = paths.current_package_build_directory
        working_directory = paths.current_package_directory / "src"
        bin_directory = build_directory / "bin"

        environment = {
            "PATH": os.environ["PATH"],
            "INSTPATH": str(build_directory)
        }

        run(
            ["make", "atomsk"],
            environment=environment,
            working_directory=working_directory
        )

        bin_directory.mkdir(parents=True)

        run(
            ["make", "install"],
            environment=environment,
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
