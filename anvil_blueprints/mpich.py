import os

from pathlib import Path
from typing import List
from urllib.parse import urlparse

from anvil import Blueprint, HttpSource, Source, run


class Mpich(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "mpich"

    @classmethod
    def source(cls) -> Source:
        return HttpSource(
            "https://www.mpich.org/static/downloads/4.0.2/mpich-4.0.2.tar.gz"
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return []

    def build(self) -> None:
        paths = self.paths
        build_directory = paths.current_package_build_directory
        working_directory = paths.current_package_directory
        archive_file_name = Path(urlparse(self.source().url).path).name
        archive_file = (
            paths.current_package_download_directory / archive_file_name
        )

        environment = {
            "PATH": os.environ["PATH"]
        }

        run(
            ["tar", "--strip-components=1", "-zxvf", str(archive_file)],
            working_directory=working_directory
        )

        run(
            ["./configure", "--enable-shared", f"--prefix={build_directory}"],
            environment={
                **environment,
                "FFLAGS": "-fallow-argument-mismatch",
                "FCFLAGS": "-fallow-argument-mismatch"
            },
            working_directory=working_directory
        )

        run(
            ["make"],
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
