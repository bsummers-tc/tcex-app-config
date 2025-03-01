"""TcEx Framework Module"""

# standard library
import re
from copy import deepcopy
from typing import ClassVar

# third-party
from pydantic import BaseModel, Field, root_validator, validator
from semantic_version import Version

from .install_json_model import (
    FeedsModel,
    InstallJsonCommonModel,
    InstallJsonOrganizationModel,
    OutputVariablesModel,
    ParamsModel,
    RetryModel,
    TypeEnum,
    snake_to_camel,
)
from .job_json_model import JobJsonCommonModel


class FeedsSpecModel(FeedsModel):
    """Model definition for app_spec.organization.feeds."""

    job: JobJsonCommonModel = Field(..., description='')


class NotesPerActionModel(BaseModel):
    """Model definition for app_spec.notes_per_action."""

    action: str = Field(..., description='The action name.')
    note: str = Field(..., description='The note describing the action.')

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OrganizationModel(InstallJsonOrganizationModel):
    """Model definition for app_spec.organization."""

    feeds: list[FeedsSpecModel] = Field([], description='')

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OutputVariablesSpecModel(OutputVariablesModel):
    """Model definition for app_spec.outputs.output_variables."""

    disabled: bool = Field(
        default=False,
        description='If True, the output will not be included in ij/lj files.',
    )
    type: str = Field(
        'String',
        description='The output variable type (e.g., String, TCEntity, etc).',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class OutputDataModel(BaseModel):
    """Model definition for app_spec.output_data."""

    display: str | None = Field(
        None,
        description='The display clause that controls visibility of the output.',
    )
    output_variables: list[OutputVariablesSpecModel] = Field(
        ...,
        description='An array of output variables.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True

    @validator('display')
    @classmethod
    def _display(cls, v: str):
        """Normalize "always True" expression for display clause."""
        if v is not None and v.lower() == "tc_action not in ('')":
            v = '1'
        return v  # pragma: no cover


class ParamsSpecModel(ParamsModel):
    """Model definition for app_spec.params."""

    display: str | None = Field(
        None,
        description='The display clause from the layout.json file.',
    )
    disabled: bool | None = Field(
        default=False,
        description='If True, the parameter will not be included in ij/lj files.',
    )
    type: TypeEnum = Field(
        TypeEnum.String,
        description='',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        fields: ClassVar = {'sequence': {'exclude': True}}
        smart_union = True
        use_enum_values = True
        validate_assignment = True


class PlaybookSpecModel(BaseModel):
    """Model definition for app_spec.playbook."""

    retry: RetryModel | None = Field(
        None,
        description='',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ReleaseNoteModel(BaseModel):
    """Model definition for app_spec.releaseNotes."""

    notes: list[str] = Field(
        ...,
        description='One or more notes for the release.',
    )
    version: str = Field(
        ...,
        description='The version of the release.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class SectionsModel(BaseModel):
    """Model definition for app_spec.sections."""

    section_name: str = Field(
        ...,
        description='The name of the section.',
    )
    params: list[ParamsSpecModel] = Field(
        ...,
        description='A list of input parameter data.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class AppSpecYmlModel(InstallJsonCommonModel):
    """Model definition for the app_spec.yml file."""

    note_per_action: list[NotesPerActionModel] | None = Field(
        None,
        description='',
    )
    organization: OrganizationModel | None = Field(
        None,
        description='A section for settings related to the organization (job) Apps.',
    )
    output_data: list[OutputDataModel] | None = Field(
        None,
        description='The outputs data for Playbook and Service Apps.',
    )
    output_prefix: str | None = Field(
        None,
        description=(
            'The prefix for output variables, used for advanced request outputs. This value '
            'should match what is passed to the advanced request method in the playbook App.'
        ),
    )
    package_name: str = Field(
        None,
        description='The package name (app_name in tcex.json) for the App.',
    )
    playbook: PlaybookSpecModel | None = Field(
        None,
        description='The playbook section of the install.json.',
    )
    internal_notes: list[str] | None = Field(
        None,
        description='Internal notes for the App.',
    )
    release_notes: list[ReleaseNoteModel] = Field(
        ...,
        description='The release notes for the App.',
    )
    schema_version: str = Field(
        '1.0.0',
        description='The version of the App Spec schema.',
    )
    sections: list[SectionsModel] = Field(
        ...,
        description='Layout sections for an App including params.',
    )
    service_details: str | None = Field(
        None, description='Optional service details for Service Apps.'
    )

    @root_validator
    @classmethod
    def _validate_no_input_duplication(cls, values):
        """Validate that no two parameters have the same name."""
        duplicates = {}
        for section in values.get('sections', []):
            for param in section.params:
                duplicates.setdefault(param.name, []).append(param.label)

        # strip out non-duplicates
        duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

        if duplicates:
            formatted_duplicates = [f'{k}({len(v)})' for k, v in duplicates.items()]
            ex_msg = f'Found duplicate parameters: {", ".join(formatted_duplicates)}'
            raise ValueError(ex_msg)
        return values

    @validator('schema_version')
    @classmethod
    def _version(cls, v: str):
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v  # pragma: no cover

    @validator('output_prefix', always=True, pre=True)
    @classmethod
    def _output_prefix(cls, v: str | None, values: dict):
        """Validate output_prefix is set when required."""
        if 'advancedRequest' in values.get('features', []):
            if v is None:
                ex_msg = (
                    'The outputPrefix field is required when feature advancedRequest is enabled.'
                )
                raise ValueError(ex_msg)
        else:
            # remove output_prefix if not required
            v = None
        return v

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True

    @property
    def inputs(self) -> list:
        """Return lj.inputs."""
        _inputs = []
        for sequence, section in enumerate(self.sections, start=1):
            # build params
            parameters = []
            for p in section.params:
                # exclude disabled and serviceConfig params
                if any([p.disabled, p.hidden, p.service_config]):
                    continue

                param = {'name': p.name}
                if p.display:
                    param['display'] = p.display

                parameters.append(param)

            if parameters:
                # append section
                _inputs.append(
                    {
                        'parameters': parameters,
                        'sequence': sequence,
                        'title': section.section_name,
                    }
                )
        return _inputs

    def get_note_per_action(self, action: str) -> NotesPerActionModel | None:
        """Return the note_per_action for the provided action."""
        for npa in self.note_per_action or []:
            if npa.action == action:
                return npa
        return None

    @property
    def note_per_action_formatted(self) -> list[str]:
        """Return formatted note_per_action."""
        _note_per_action = ['\n\nThe following actions are included:']
        _note_per_action.extend(
            [f'-   **{npa.action}** - {npa.note}' for npa in self.note_per_action or []]
        )
        return _note_per_action

    @property
    def outputs(self) -> list[OutputVariablesModel]:
        """Return lj.outputs."""
        _outputs = []
        for output_data in self.output_data or []:
            for output_variable in output_data.output_variables:
                if output_variable.disabled is True:
                    continue

                _outputs.append(
                    {
                        'display': output_data.display,
                        'name': output_variable.name,
                    }
                )
        return _outputs

    @property
    def output_variables(self) -> list[OutputVariablesModel]:
        """Return ij.playbook.outputVariables."""
        return [
            ov
            for output in self.output_data or []
            for ov in output.output_variables or []
            if ov.disabled is False
        ]

    @property
    def params(self) -> list[ParamsSpecModel]:
        """Return ij.params."""
        _params = []
        sequence = 1
        for section in deepcopy(self.sections):
            for param in section.params:
                if param.disabled is True:
                    continue

                # set default playbookDataType for String type params
                self._set_default_playbook_data_type(param)

                # set default validValues for String type params
                self._set_default_valid_values(param)

                # remove the disabled field (not supported in install.json)
                param.disabled = None

                # remove the display field (not supported in install.json)
                param.display = None

                # add the sequence number
                param.sequence = sequence

                _params.append(param)

                # increment sequence
                sequence += 1
        return _params

    @property
    def release_notes_formatted(self) -> list[str]:
        """Return readme_md.releaseNotes."""
        _release_notes = ['## Release Notes']
        _release_notes.append('')

        # try to sort release notes by version.  If we encounter any issues, just use release_notes
        try:
            sorted_releases = sorted(
                (r for r in self.release_notes),
                key=lambda r: Version(re.match(r'^\d+.\d+.\d+', r.version)[0]),  # type: ignore
                reverse=True,
            )
        except Exception:
            sorted_releases = self.release_notes

        for release_note in sorted_releases:
            _release_notes.append(f'### {release_note.version}')
            _release_notes.append('')
            _release_notes.extend([f'-   {rn}' for rn in release_note.notes])
            _release_notes.append('')
        return _release_notes

    @property
    def requires_layout(self):
        """Return True if App requires a layout.json file."""
        if self.runtime_level.lower() in ['apiservice', 'feedapiservice', 'organization']:
            return False

        for section in self.sections:
            for param in section.params:
                if param.display:
                    return True

        for output_data in self.output_data or []:
            if output_data.display not in [None, '1', '']:
                return True

        return False

    def _set_default_playbook_data_type(self, param: ParamsSpecModel):
        """Set default playbookDataType for String type params.

        Playbook Data Types rule:
          * Input type is "String"
          * No "playbookDataType" values are provided
        """
        # by rule any input of type String must have String and playbookDataType
        if self.runtime_level.lower() == 'playbook' and (
            param.type in ['EditChoice', 'KeyValueList', 'String'] and not param.playbook_data_type
        ):
            param.playbook_data_type = ['String']

    def _set_default_valid_values(self, param: ParamsSpecModel):
        """Set default playbookDataType for String type params.

        Valid Values rule:
          * Input type is "String"
          * No "validValues" values are provided
          * The playbookDataType supports String
        """
        if (
            param.type in ['KeyValueList', 'String']
            and not param.valid_values
            and (
                'String' in param.playbook_data_type
                or self.runtime_level.lower()
                in ['organization', 'triggerservice', 'webhooktriggerservice']
            )
        ):
            param.valid_values = ['${TEXT}']
            if param.encrypt is True:
                param.valid_values = ['${KEYCHAIN}']
