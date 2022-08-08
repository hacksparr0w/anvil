import os
from posix import environ

from typing import List

from anvil import Blueprint, GitSource, Source, run


class Lammps(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "lammps"

    @classmethod
    def source(cls) -> Source:
        return GitSource(
            "https://github.com/lammps/lammps.git",
            branch="stable"
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return []

    def build(self) -> None:
        working_directory = self.paths.current_package_directory / "src"
        make_file = (
            working_directory
            / "MAKE"
            /  "OPTIONS"
            / f"Makefile.g++_mpich"
        )

        environment = {"PATH": os.environ["PATH"]}

        run(
            ["make", "yes-openmp"],
            environment=environment,
            working_directory=working_directory
        )

        run(
            [
                "sed",
                "-i",
                "-E",
                r"s/(CCFLAGS|LINKFLAGS) =(.+?)$/\1 =\2 -fopenmp/",
                str(make_file)
            ],
            environment=environment,
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_directory.is_dir()
