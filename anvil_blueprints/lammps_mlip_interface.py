import os

from typing import List

from anvil import Blueprint, GitSource, Source, run


class LammpsMlipInterface(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "lammps-mlip-interface"

    @classmethod
    def source(cls) -> Source:
        return GitSource(
            "https://gitlab.com/ashapeev/interface-lammps-mlip-2.git"
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return ["mpich", "lammps", "mlip"]

    def build(self) -> None:
        paths = self.paths
        working_directory = paths.current_package_directory
        current_package_bin_directory = (
            paths.current_package_build_directory / "bin"
        )

        lammps_package_directory = (
            paths.of("lammps").current_package_directory
        )

        mpich_bin_directory = (
            paths.of("mpich").current_package_build_directory
            / "bin"
        )

        lammps_build_target = "g++_mpich"
        lammps_executable_file = (
            working_directory
            / f"lmp_{lammps_build_target}"
        )

        mlip_interface_file = (
            paths.of("mlip").current_package_build_directory
            / "lib"
            / "lib_mlip_interface.a"
        )

        environment = {
            "PATH": f"{mpich_bin_directory}:{os.environ['PATH']}"
        }

        run(
            ["cp", str(mlip_interface_file), "./"],
            working_directory=working_directory
        )

        run(
            [
                "./install.sh",
                str(lammps_package_directory),
                lammps_build_target
            ],
            environment=environment,
            working_directory=working_directory
        )

        current_package_bin_directory.mkdir(parents=True)
        lammps_executable_link = current_package_bin_directory / "lmp"

        run(
            [
                "ln",
                "-s",
                str(lammps_executable_file),
                str(lammps_executable_link)
            ],
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
