from typing import List

from anvil import Blueprint, HttpSource, run


class Ovito(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "ovito"

    @classmethod
    def source(cls) -> HttpSource:
        return HttpSource(
            "https://www.ovito.org/download/3106/",
            file_name="ovito-basic-3.7.8-x86_64.tar.xz"
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return []

    def build(self) -> None:
        paths = self.paths
        build_directory = paths.current_package_build_directory
        archive_file = (
            paths.current_package_download_directory
            / self.source().file_name
        )

        build_directory.mkdir()

        run(
            ["tar", "--strip-components=1", "-xvf", str(archive_file)],
            working_directory=build_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
