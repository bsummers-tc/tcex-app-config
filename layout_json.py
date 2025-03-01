"""TcEx Framework Module"""

# standard library
import json
import logging
from collections import OrderedDict
from functools import cached_property
from pathlib import Path

from ...pleb.singleton import Singleton
from .model.install_json_model import OutputVariablesModel, ParamsModel
from .model.layout_json_model import LayoutJsonModel

# get logger
_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])


class LayoutJson(metaclass=Singleton):
    """Config object for layout.json configuration file"""

    def __init__(
        self,
        filename: str | None = None,
        path: Path | str | None = None,
        logger: logging.Logger | None = None,
    ):
        """Initialize instance properties."""
        filename = filename or 'layout.json'
        path = Path(path or Path.cwd())
        self.log = logger or _logger

        # properties
        self.fqfn = path / filename

    @cached_property
    def contents(self) -> dict:
        """Return layout.json file contents."""
        contents = {}
        if self.fqfn.is_file():
            try:
                with self.fqfn.open() as fh:
                    contents = json.load(fh, object_pairs_hook=OrderedDict)
            except (OSError, ValueError):  # pragma: no cover
                self.log.exception(
                    f'feature=layout-json, exception=failed-reading-file, filename={self.fqfn}'
                )
        else:  # pragma: no cover
            self.log.error(f'feature=layout-json, exception=file-not-found, filename={self.fqfn}')
        return contents

    def create(self, inputs: list[ParamsModel], outputs: list[OutputVariablesModel]):
        """Create new layout.json file based on inputs and outputs."""

        def input_data(sequence: int, title: str) -> dict:
            return {
                'parameters': [],
                'sequence': sequence,
                'title': title,
            }

        lj = LayoutJsonModel(
            inputs=[
                input_data(1, 'Action'),
                input_data(2, 'Connection'),
                input_data(3, 'Configure'),
                input_data(4, 'Advanced'),
            ],  # type: ignore
            outputs=[{'display': '', 'name': o.name} for o in outputs],  # type: ignore
        )

        for input_ in inputs:
            if input_.name == 'tc_action':
                lj.inputs[0].parameters.append({'name': 'tc_action'})  # type: ignore
            elif input_.hidden is True:
                lj.inputs[2].parameters.append(
                    {
                        'display': "'hidden' != 'hidden'",
                        'hidden': 'true',
                        'name': input_.name,
                    }  # type: ignore
                )
            else:
                lj.inputs[2].parameters.append({'display': '', 'name': input_.name})  # type: ignore

        # write layout file to disk
        data = lj.json(
            by_alias=True, exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True
        )
        self.write(data)

    @property
    def has_layout(self):
        """Return True if App has layout.json file."""
        return self.fqfn.is_file()

    @cached_property
    def model(self) -> LayoutJsonModel:
        """Return the Install JSON model."""
        return LayoutJsonModel(**self.contents)

    @property
    def update(self):
        """Return InstallJsonUpdate instance."""
        return LayoutJsonUpdate(lj=self)

    def write(self, data: str):
        """Write updated file.

        Args:
            data: The JSON string to write data.
        """
        with self.fqfn.open(mode='w') as fh:
            fh.write(f'{data}\n')


class LayoutJsonUpdate:
    """Update layout.json file with current standards and schema."""

    def __init__(self, lj: LayoutJson):
        """Initialize instance properties."""
        self.lj = lj

    def multiple(self):
        """Update the layouts.json file."""
        # APP-86 - sort output data by name
        self.update_sort_outputs()

        data = self.lj.model.json(
            by_alias=True, exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True
        )
        self.lj.write(data)

    def update_sort_outputs(self):
        """Sort output field by name."""
        # APP-86 - sort output data by name
        self.lj.model.outputs = sorted(
            self.lj.model.dict().get('outputs', []),
            key=lambda i: i['name'],  # type: ignore
        )
