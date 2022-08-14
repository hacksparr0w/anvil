from typing import List

from anvil import Blueprint, HttpSource, run


class Bazelisk(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "bazelisk"

    @classmethod
    def source(cls) -> HttpSource:
        return HttpSource.from_url(
            "https://github.com/bazelbuild/bazelisk"
            "/releases/download/v1.12.0/bazelisk-linux-amd64"
        )

    @classmethod
    def dependencies(cls) -> List[str]:
        return []

    def build(self) -> None:
        paths = self.paths
        bin_directory = paths.current_package_build_directory / "bin"
        working_directory = paths.current_package_directory
        executable_file_name = self.source().file_name
        executable_file = (
            paths.current_package_download_directory / executable_file_name
        )

        executable_link = bin_directory / "bazel"

        bin_directory.mkdir(parents=True)

        run(
            ["ln", "-s", str(executable_file), str(executable_link)],
            working_directory=working_directory
        )

        run(["chmod", "+x", str(executable_link)])

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
