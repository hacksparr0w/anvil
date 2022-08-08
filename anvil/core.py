import importlib.util
import inspect

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Optional, Type
from urllib.parse import urlparse

from .utility import clone_git_repository, download_file, pythonify_name


__all__ = [
    "Blueprint",
    "GitSource",
    "HttpSource",
    "Source",
    "Paths",

    "install",
    "load_blueprint",
]


class Paths:
    def __init__(
        self,
        package_directory: Path,
        current_package_directory: Path
    ) -> None:
        self.package_directory = package_directory
        self.current_package_directory = current_package_directory

    @property
    def current_package_build_directory(self):
        return self.current_package_directory / "build"

    @property
    def current_package_download_directory(self):
        return self.current_package_directory / "downloads"

    def of(self, name: str) -> "Paths":
        return type(self).of(self.package_directory, name)

    @classmethod
    def of(cls, package_directory: Path, name: str) -> "Paths":
        current_package_directory = package_directory / name

        return cls(package_directory, current_package_directory)


class Source(metaclass=ABCMeta):
    @abstractmethod
    def fetch(self, blueprint: "Blueprint", *args, **kwargs) -> None:
        raise NotImplemented

    @abstractmethod
    def is_fetched(self, blueprint: "Blueprint", *args, **kwargs) -> bool:
        raise NotImplemented


class HttpSource(Source):
    def __init__(self, url: str) -> None:
        super().__init__()

        self.url = url

    def fetch(self, blueprint: "Blueprint") -> None:
        url = self.url
        download_directory = (
            blueprint.paths.current_package_download_directory
        )

        download_directory.mkdir(parents=True, exist_ok=True)

        file_name = Path(urlparse(url).path).name
        path = download_directory / file_name

        download_file(url, path)

    def is_fetched(self, blueprint: "Blueprint") -> None:
        file_name = Path(urlparse(self.url).path).name
        path = blueprint.paths.current_package_download_directory / file_name

        return path.is_file()


class GitSource(Source):
    def __init__(
        self,
        url: str,
        branch: Optional[str] = None,
        depth: Optional[int] = None
    ) -> None:
        super().__init__()

        self.url = url
        self.branch = branch
        self.depth = depth

    def fetch(self, blueprint: "Blueprint") -> None:
        clone_git_repository(
            self.url,
            blueprint.paths.current_package_directory,
            branch=self.branch,
            depth=self.depth
        )

    def is_fetched(self, blueprint: "Blueprint") -> None:
        return blueprint.paths.current_package_directory.is_dir()


class Blueprint(metaclass=ABCMeta):
    def __init__(self, paths: Paths) -> None:
        self.paths = paths

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        raise NotImplemented

    @classmethod
    @abstractmethod
    def source(cls) -> Source:
        raise NotImplemented

    @classmethod
    @abstractmethod
    def dependencies(cls) -> List[str]:
        raise NotImplemented

    @abstractmethod
    def build(self) -> None:
        raise NotImplemented

    @abstractmethod
    def is_built(self) -> bool:
        raise NotImplemented


def load_blueprint(path: Path) -> Type[Blueprint]:
    name = f"anvil.blueprint.{path.stem}"
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    classes = inspect.getmembers(
        module, lambda x: inspect.isclass(x)
            and issubclass(x, Blueprint)
            and x is not Blueprint
    )

    if len(classes) == 0:
        raise RuntimeError(
            f"No subclass of the Blueprint type found in '{path}'"
        )

    if len(classes) > 1:
        raise RuntimeError(
            f"Too many subclasses of the Blueprint type found in '{path}'"
        )

    blueprint = classes[0][1]

    return blueprint


def install(
    blueprint_directory: Path,
    package_directory: Path,
    name: str
) -> None:
    pythonified_name = pythonify_name(name)
    blueprint_file_name = pythonified_name + ".py"
    blueprint_file = blueprint_directory / blueprint_file_name

    if not blueprint_file.is_file():
        raise FileNotFoundError(f"No blueprint found for {name}")

    blueprint = load_blueprint(blueprint_file)
    paths = Paths.of(package_directory, name)
    instance = blueprint(paths)

    if instance.is_built():
        print(f"{name} is already installed.")
        return

    # TODO: Check dependencies

    if not package_directory.is_dir():
        package_directory.mkdir()

    source = instance.source()

    if not source.is_fetched(instance):
        print(f"Fetching {name}...")
        source.fetch(instance)

    print(f"Building {name}...")

    instance.build()

    print(f"{name} built successfully.")
