import os

from typing import List

from anvil import Blueprint, Source, GitSource, run


class DeepMdKit(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "deepmd-kit"

    @classmethod
    def source(cls) -> Source:
        return GitSource(
            "https://github.com/deepmodeling/deepmd-kit.git",
            recursive=True
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["lammps", "tensorflow"]

    def build(self) -> None:
        paths = self.paths
        build_directory = paths.current_package_build_directory
        working_directory = (
            paths.current_package_directory / "source" / "build"
        )

        tensorflow_build_directory = (
            paths.of("tensorflow").current_package_build_directory
        )

        lammps_source_directory = (
            paths.of("lammps").current_package_directory
        )

        environment = {"PATH": os.environ["PATH"]}

        working_directory.mkdir()

        run(
            [
                "cmake",
                f"-DTENSORFLOW_ROOT={tensorflow_build_directory}",
                f"-DCMAKE_INSTALL_PREFIX={build_directory}",
                f"-DLAMMPS_SOURCE_ROOT={lammps_source_directory}",
                ".."
            ],
            environment=environment,
            working_directory=working_directory
        )

        run(
            ["make", "-j4"],
            environment=environment,
            working_directory=working_directory
        )

        run(
            ["make", "install"],
            environment=environment,
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
