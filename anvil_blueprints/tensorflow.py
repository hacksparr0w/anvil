import os

from typing import List

from anvil import Blueprint, GitSource, run


class Tensorflow(Blueprint):
    @classmethod
    def name(cls) -> str:
        return "tensorflow"

    @classmethod
    def source(cls) -> GitSource:
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
        build_directory = paths.current_package_build_directory
        working_directory = paths.current_package_directory
        bazelisk_bin_directory = (
            paths.of("bazelisk").current_package_build_directory / "bin"
        )

        include_directory = build_directory / "include"
        lib_directory = build_directory / "lib"

        environment = {
            "PATH": f"{bazelisk_bin_directory}:{os.environ['PATH']}",
            "HOME": os.environ["HOME"]
        }

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

        include_directory.mkdir(parents=True)
        lib_directory.mkdir()

        library_paths = working_directory.glob("./bazel-bin/**/lib*.so*")

        for library_path in library_paths:
            run(
                ["cp", "-d", library_path, str(lib_directory)],
                working_directory=working_directory
            )

        run(
            [
                "rsync",
                "-avzhm",
                "--exclude",
                "_virtual_includes/",
                "--include",
                "*/",
                "--include",
                "*.h",
                "--include",
                "*.inc",
                "--exclude",
                "*",
                "bazel-bin/",
                str(include_directory)
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*.h",
                "--include",
                "*.inc",
                "--exclude",
                "*",
                "tensorflow/cc",
                str(include_directory / "tensorflow")
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*.h",
                "--include",
                "*.inc",
                "--exclude",
                "*",
                "tensorflow/core",
                str(include_directory / "tensorflow")
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*",
                "--exclude",
                "*.cc",
                "third_party/",
                str(include_directory / "third_party")
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*",
                "--exclude",
                "*.txt",
                "bazel-tensorflow/external/eigen_archive/Eigen/",
                str(include_directory / "Eigen")
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*",
                "--exclude",
                "*.txt",
                "bazel-tensorflow/external/eigen_archive/unsupported/",
                str(include_directory / "unsupported")
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*.h",
                "--include",
                "*.inc",
                "--exclude",
                "*",
                "bazel-tensorflow/external/com_google_protobuf/src/google/",
                str(include_directory / "google")
            ],
            working_directory=working_directory
        )

        run(
            [
                "rsync",
                "-avzhm",
                "--include",
                "*/",
                "--include",
                "*.h",
                "--include",
                "*.inc",
                "--exclude",
                "*",
                "bazel-tensorflow/external/com_google_absl/absl/",
                str(include_directory / "absl")
            ],
            working_directory=working_directory
        )

    def is_built(self) -> bool:
        return self.paths.current_package_build_directory.is_dir()
