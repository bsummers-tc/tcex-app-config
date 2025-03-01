"""TcEx Framework Module"""

# standard library
import contextlib
import logging
import os
import platform
import re
import uuid
from enum import Enum
from importlib.metadata import version as get_version
from pathlib import Path

# third-party
from pydantic import BaseModel, Field, validator
from pydantic.types import UUID4, UUID5, constr
from semantic_version import Version

__all__ = ['InstallJsonModel']

# get logger
_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# define JSON encoders
json_encoders = {Version: str, UUID4: str, UUID5: str}


class _FeatureModel(BaseModel):
    """Model definition"""

    default: bool | None = Field(
        default=False, description='Indicates whether the feature is a default for the App type.'
    )
    runtime_levels: list[str] | None = Field(
        None,
        description='The runtime levels that the feature is valid for.',
    )
    version: Version | None = Field(
        None,
        description='The version of TcEx that the feature was added.',
    )

    class Config:
        """DataModel Config"""

        arbitrary_types_allowed = True
        json_encoders = json_encoders


class DeprecationModel(BaseModel):
    """Model definition for install_json.deprecation"""

    indicator_type: str | None = Field(
        None,
        description='The indicator type for the deprecation rule.',
    )
    interval_days: int | None = Field(
        None,
        description='The frequency the deprecation rule should run.',
    )
    confidence_amount: int | None = Field(
        None,
        description='The amount the confidence should be reduced by.',
    )
    delete_at_minimum: bool = Field(
        default=False,
        description='If true, the indicator will be deleted at the minimum confidence.',
    )
    percentage: bool = Field(
        default=False,
        description='If true, use percentage instead of point value when reducing the confidence.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class FirstRunParamsModel(BaseModel):
    """Model definition for install_json.deprecation"""

    param: str | None = Field(
        None,
        description='The parameter to set to the first run value.',
    )
    value: int | str | None = Field(
        None,
        description='The value to set the parameter to.',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class FeedsModel(BaseModel):
    """Model definition for install_json.feeds"""

    attributes_file: str | None = Field(
        None,
        description=(
            'Optional property that provides the name of the CSV file with any custom '
            'Attributes required for the feed (e.g., attribute.json).'
        ),
    )
    deprecation: list[DeprecationModel] = Field(
        [],
        description='The deprecation rules for the feed.',
    )
    document_storage_limit_mb: int = Field(
        ...,
        description='Optional property that sets the Document storage limit.',
    )
    enable_bulk_json: bool = Field(
        default=False,
        description='Optional property that enables or disables the bulk JSON capability.',
    )
    first_run_params: list[FirstRunParamsModel] = Field(
        [],
        description='Param overrides for the first run of the feed.',
    )
    indicator_limit: int = Field(
        ...,
        description='Optional property that sets the Indicator limit.',
    )
    job_file: str = Field(
        ...,
        description=(
            'Optional property that provides the name of the JSON file that is used to '
            'set up and run the Job that pulls in content from the feed.'
        ),
    )
    source_category: str = Field(
        ...,
        description='Optional property that specifies how the source should be categorized.',
    )
    source_description: str = Field(
        ...,
        description=(
            "Optional property that provides the source's description as it will be "
            'displayed in the ThreatConnect platform.'
        ),
    )
    source_name: str = Field(
        ...,
        description=(
            "Optional property that provides the name of the source in which the feed's "
            'content will be created.'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ExposePlaybookKeyAsEnum(str, Enum):
    """Enum for install_json.params[].exposePlaybookAs"""

    Binary = 'Binary'
    BinaryArray = 'BinaryArray'
    KeyValue = 'KeyValue'
    KeyValueArray = 'KeyValueArray'
    String = 'String'
    StringArray = 'StringArray'
    TCEntity = 'TCEntity'
    TCEntityArray = 'TCEntityArray'


class TypeEnum(str, Enum):
    """Enum for install_json.params[].type"""

    Boolean = 'Boolean'
    Choice = 'Choice'
    EditChoice = 'EditChoice'
    KeyValueList = 'KeyValueList'
    MultiChoice = 'MultiChoice'
    String = 'String'
    StringMixed = 'StringMixed'


class ParamsModel(BaseModel):
    """Model definition for install_json.params"""

    allow_multiple: bool = Field(
        default=False,
        description=(
            'The value of this optional property is automatically set to true if the '
            'MultiChoice type is used. If a String type is used, this flag allows the '
            'user to define multiple values in a single input field delimited by a pipe '
            '("|") character.'
        ),
    )
    allow_nested: bool = Field(
        default=False,
        description='',
    )
    default: bool | str | None = Field(
        None,
        description='Optional property that is the default value for an App input parameter.',
    )
    encrypt: bool = Field(
        default=False,
        description=(
            'Optional property that designates a parameter as an encrypted value. '
            'Parameters defined as encrypted will be managed by the Keychain feature '
            'that encrypts password while at rest. This flag should be used with the '
            'String type and will render a password input text box in the App '
            'configuration.'
        ),
    )
    expose_playbook_key_as: ExposePlaybookKeyAsEnum | None = Field(
        None,
        description='',
    )
    feed_deployer: bool = Field(
        default=False,
        description='',
    )
    hidden: bool = Field(
        default=False,
        description=(
            'If this optional property is set to true, this parameter will be hidden '
            'from the Job Wizard. Hidden parameters allow the developer to persist '
            'parameters between Job executions without the need to render the values in '
            'the Job Wizard. This option is valid only for Python and Java Apps. Further '
            'details on persisting parameters directly from the app are beyond the scope '
            'of this documentation.'
        ),
    )
    intel_type: list[str] = Field(
        [],
        description='',
    )
    label: str = Field(
        ...,
        description=(
            'Required property providing a description of the parameter displayed in the '
            'Job Wizard or Spaces Configuration dialog box within the ThreatConnect '
            'platform.'
        ),
    )
    name: str = Field(
        ...,
        description=(
            'Required property that is the internal parameter name taken from the Job '
            'Wizard and passed to the App at runtime. It is the effective command-line '
            'argument name passed to the App.'
        ),
    )
    note: str | None = Field(
        None,
        description=(
            'Optional parameter-description field available in Playbook Apps under the ? '
            'tooltip when the App parameters are being edited. Use this field to '
            'describe the purpose of the parameter in two to three sentences.'
        ),
    )
    playbook_data_type: list[str] = Field(
        [],
        description=(
            'Optional property restricting the data type of incoming Playbook variables. '
            'This is different than the type property that controls the UI input type. '
            'The playbookDataType can be any standard or custom type and is expected to '
            'be an array of strings.'
        ),
    )
    required: bool = Field(
        default=False,
        description=(
            'Optional property designating this parameter as a required field that must '
            'be populated to save the Job or Playbook App.'
        ),
    )
    sequence: int | None = Field(
        None,
        description=(
            'Optional number used to control the ordering of the parameters in the Job '
            'Wizard or Spaces Configuration dialog box. If it is not defined, the order '
            'of the parameters in the install.json file will be used.'
        ),
    )
    service_config: bool = Field(
        default=False,
        description='',
    )
    setup: bool = Field(
        default=False,
        description='',
    )
    type: TypeEnum = Field(
        ...,
        description=(
            'Required property to enable the UI to display relevant components and allow '
            'the Job Executor to adapt how parameters are passed to an App at runtime. '
            'The table below lists the available types and how they affect elements '
            'within the platform.'
        ),
    )
    valid_values: list[str] = Field(
        [],
        description=(
            'Optional property to be used with the Choice, MultiChoice, and String input '
            'types to provide pre-defined inputs for the user selection.'
        ),
    )
    view_rows: int | None = Field(
        None,
        description=(
            'Optional property for Playbook Apps to control the height of the display in '
            'the input parameter, and it expects an integer value. A value of 1 is '
            'default (and will show a text input element) and anything greater than 1 '
            'displays a textarea input when editing the Playbook App in ThreatConnect.'
        ),
    )

    @validator('name')
    @classmethod
    def _name(cls, v):
        """Return the transformed "name" field.

        Used to replace labels for fields non-alphanumeric chars (migrate label to name).
        """
        if v is not None:
            v = v.lower().replace(' ', '_')

            # remove all non-alphanumeric characters and underscores
            v = re.sub(r'[^a-zA-Z0-9_]', '', v)
        return v

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        smart_union = True
        use_enum_values = True
        validate_assignment = False

    def __hash__(self):
        """Make model hashable."""
        return hash(self.name)


class OutputVariablesModel(BaseModel):
    """Model definition for install_json.playbook.outputVariables"""

    # sensitive value
    encrypt: bool = Field(
        default=False,
        description='',
    )
    intel_type: list | None = Field(
        None,
        description='',
    )
    name: str = Field(
        ...,
        description='',
    )
    note: str | None = Field(
        None,
        description='',
    )
    type: str = Field(
        ..., description='Required property that specifies the type of the output variable.'
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True

    def __hash__(self):
        """Make model hashable."""
        return hash(f'{self.name}{self.type}')


class RetryModel(BaseModel):
    """Model definition for install_json.playbook.retry"""

    actions: list[str] = Field(
        [],
        description='A list of tc_actions that support retry.',
    )
    allowed: bool = Field(
        default=False,
        description=(
            'Optional property that specifies whether the Playbook App can retry its execution.'
        ),
    )
    default_delay_minutes: int = Field(
        ...,
        description=(
            'Optional property that specifies the number of minutes between each new '
            'retry in case of failure. This property assumes that the allowed property '
            'is set to true to allow the App to retry.'
        ),
    )
    default_max_retries: int = Field(
        ...,
        description=(
            'Optional property that specifies the maximum number of times the Playbook '
            'App can retry in case of failure. This property assumes that the allowed '
            'property is set to true to allow the app to retry.'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class PlaybookModel(BaseModel):
    """Model definition for install_json.playbook"""

    output_prefix: str | None = Field(None, description='')
    output_variables: list[OutputVariablesModel] = Field(
        [],
        description=(
            'Optional outputVariables property that specifies the variables that a '
            'Playbook App will provide for downstream Playbooks.'
        ),
    )
    retry: RetryModel | None = Field(
        None,
        description=(
            'Optional retry property that can be used to allow a Playbook to retry its '
            'execution in case of failure.'
        ),
    )
    type: str = Field(
        ...,
        description='The App category (e.g., Endpoint Detection and Response).',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class ServiceModel(BaseModel):
    """Model definition for install_json.service"""

    discovery_types: list[str] = Field(
        [],
        description='Service App discovery types (e.g., TaxiiApi).',
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


def get_commit_hash() -> str | None:
    """Return the current commit hash if available.

    This is not a required task so best effort is fine. In other words this is not guaranteed
    to work 100% of the time.
    """
    commit_hash = None
    branch = None
    branch_file = Path('.git') / 'HEAD'  # ref: refs/heads/develop

    # get current branch
    if branch_file.is_file():
        with branch_file.open(encoding='utf-8') as f, contextlib.suppress(IndexError):
            branch = '/'.join(f.read().strip().split('/')[2:])

        # get commit hash
        if branch:
            hash_file = Path('.git') / 'refs' / 'heads' / branch
            if hash_file.is_file():
                with hash_file.open(encoding='utf-8') as f:
                    commit_hash = f.read().strip()

    if commit_hash is None:
        # gitlab / github CI environment variable
        commit_hash = os.getenv('CI_COMMIT_SHA') or os.getenv('GITHUB_SHA')

    return commit_hash


def gen_app_id() -> UUID5:
    """Return a generate id for the current App."""
    return uuid.uuid4()


class InstallJsonCommonModel(BaseModel):
    """Model definition for install.json common configuration

    This model contains the common fields for the install.json file and
    the app_spec.yaml file.
    """

    allow_on_demand: bool = Field(
        default=False,
        description=(
            'Required property that allows or disallows an App to be run on demand using '
            'the Run Now button when the App is configured as a Job in the ThreatConnect '
            'platform. This property only applies to Python and Java Apps.'
        ),
    )
    allow_run_as_user: bool = Field(
        default=False,
        description='Controls whether a Playbook App supports run-as-users.',
    )
    api_user_token_param: bool = Field(
        default=True,
        description=(
            '[Deprecated] Optional property that specifies whether or not the App should '
            'use an API user token (which allows access to the DataStore).'
        ),
    )
    app_id: UUID4 | UUID5 = Field(
        default_factory=gen_app_id,
        description=(
            '[TcEx 1.1.4+] A unique identifier for the App. This field is not currently '
            'used in the core product, but will be used in other tooling to identify the '
            'App. The appId field with the major version from programVersion make up a '
            'unique Application release. If this field does not exist while packaging '
            'the App via the `tcex package` command, a value will be added using the '
            'project directory name as a seed. Once an App has been released the appId '
            'field should not be changed.'
        ),
    )
    category: str = Field(
        '',
        description='The category of the App. Also playbook.type for playbook Apps.',
    )
    deprecates_apps: list[str] = Field(
        [],
        description=(
            'Optional property that provides a list of Apps that should be deprecated by this App.'
        ),
    )
    display_name: constr(min_length=3, max_length=100) = Field(  # type: ignore
        ...,
        description=(
            'Required property providing the name of the App as it will be displayed in '
            'the ThreatConnect platform.'
        ),
    )
    display_path: constr(min_length=3, max_length=100) | None = Field(  # type: ignore
        None,
        description='The display path for API service Apps.',
    )
    features: list[str] = Field(
        ...,
        description=(
            'An array of supported features for the App. These feature enable '
            'additional functionality in the Core Platform and/or for the App.'
        ),
    )
    labels: list[str] = Field(
        [],
        description='A list of labels for the App.',
    )
    language_version: str = Field(
        ...,
        description=(
            'The major.minor version of the language (e.g., Python "3.11"). This value is used by '
            'the Core platform to control which version of Python is used to launch the App.'
        ),
    )
    list_delimiter: str = Field(
        ...,
        description=(
            'Optional property that sets the character used to delimit the values of '
            'an input that support the allowMultiple param option.'
        ),
    )
    min_server_version: Version = Field(
        '7.2.0',
        description=(
            'Optional string property restricting the ThreatConnect instance from '
            'installing the App if it does not meet this version requirement (e.g., 7.2.0).'
        ),
    )
    note: str | None = Field(
        None,
        description=(
            'Optional property available in Playbook Apps while configuring App inputs '
            'in the UI. This is the top level not of the App and should describe the '
            'functionality and use cases of the App.'
        ),
    )
    program_language: str = Field(
        ...,
        description=(
            'Required property describing the language runtime environment used by the '
            'ThreatConnect Job Executor. It is relevant for Apps that run on the Job '
            'Execution Engine (Python and Java Apps) and can be set to NONE for Spaces '
            'Apps.'
        ),
    )
    program_main: str = Field(
        ...,
        description=(
            'Required property providing the entry point into the App. For Python Apps, '
            'it is the name of the .py file (or exclude the extension if running it as a '
            'module). For Java Apps, it is the main class the Job Execution Engine '
            'should use when calling the App using the Java Runtime Environment.'
        ),
    )
    program_version: Version = Field(
        ...,
        description=(
            'Required property providing the version number for the App that will be '
            'displayed in the Installed Apps section available to a System '
            'Administrator. ThreatConnect recommends the use of semantic versioning '
            '(e.g., 1.0.1).'
        ),
    )
    runtime_level: str = Field(
        ...,
        description='The type for the App (e.g., Playbook, Organization, etc).',
    )
    service: ServiceModel | None = Field(
        None,
        description='',
    )
    sdk_version: Version | None = Field(
        None,
        description=(
            'The version of the SDK (TcEx). This value is used by the Core '
            'platform to control behavior in App Builder.'
        ),
    )

    @validator('language_version', always=True, pre=True)
    @classmethod
    def _language_version(cls, v) -> str:
        """Return a version object for "version" field."""

        def _major_minor(v):
            """Return the major.minor version."""
            with contextlib.suppress(Exception):
                version_ = Version.coerce(v)
                v = f'{version_.major}.{version_.minor}'
            return v

        return _major_minor(platform.python_version()) if v is None else _major_minor(v)

    @validator('min_server_version', pre=True)
    @classmethod
    def _min_server_version(cls, v) -> Version:
        """Return a version object for "version" fields."""
        # all tcex 4 Apps must have min server version of at least 7.2.0
        if v is None or Version.coerce(v) < Version('7.2.0'):
            v = '7.2.0'
        return Version.coerce(v)

    @validator('program_version', pre=True)
    @classmethod
    def _program_version(cls, v) -> Version:
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v

    @validator('sdk_version', always=True, pre=True)
    @classmethod
    def _sdk_version(cls, v) -> Version:
        """Return a version object for "version" field."""
        if v is None:
            # assume legacy App
            return Version('2.0.0')

        # ensure v is a Version object
        v = v if isinstance(v, Version) else Version.coerce(v)

        # update version
        if v >= Version('4.0.0'):
            try:
                # best effort to update the tcex version
                return Version.coerce(get_version('tcex'))
            except Exception:
                return v

        return v

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        json_encoders = json_encoders
        validate_assignment = True

    @property
    def is_api_service_app(self) -> bool:
        """Return True if the current App is ANY type of API Service App."""
        return self.runtime_level.lower() in [
            'apiservice',
            'feedapiservice',
        ]

    @property
    def is_feed_app(self) -> bool:
        """Return True if the current App is ANY type of API Service App."""
        return self.runtime_level.lower() in [
            'feedapiservice',
            'organization',
        ]

    @property
    def is_job_app(self) -> bool:
        """Return True if the current App is an Organization (job) App."""
        return self.is_organization_app

    @property
    def is_organization_app(self) -> bool:
        """Return True if the current App is an Organization (job) App."""
        return self.runtime_level.lower() == 'organization'

    @property
    def is_playbook_app(self) -> bool:
        """Return True if the current App is a Playbook App."""
        return self.runtime_level.lower() == 'playbook'

    @property
    def is_trigger_app(self) -> bool:
        """Return True if the current App is trigger Service App."""
        return self.runtime_level.lower() in ['triggerservice', 'webhooktriggerservice']

    @property
    def is_webhook_trigger_app(self) -> bool:
        """Return True if the current App is a webhook Service App."""
        return self.runtime_level.lower() == 'webhooktriggerservice'

    @property
    def is_service_app(self) -> bool:
        """Return True if the current App is ANY type of Service App."""
        return self.runtime_level.lower() in [
            'apiservice',
            'feedapiservice',
            'triggerservice',
            'webhooktriggerservice',
        ]

    @property
    def known_features(self) -> dict[str, _FeatureModel]:
        """Return all known features."""

        feature_data = {
            'advancedRequest': {
                'runtime_levels': ['playbook'],
            },
            'appBuilderCompliant': {
                'default': True,
                'runtime_levels': ['playbook', 'triggerservice', 'webhooktriggerservice'],
            },
            'CALSettings': {},
            'fileParams': {
                'default': True,
            },
            # 2025-01-22 - bcs uncommented to prevent warning
            'layoutEnabledApp': {
                'runtime_levels': ['playbook', 'triggerservice', 'webhooktriggerservice'],
            },
            'linkApiPath': {
                'runtime_levels': ['apiservice', 'feedapiservice'],
            },
            'redisPasswordSupport': {
                'default': True,
                'version': Version('3.0.9'),
            },
            'runtimeVariables': {
                'default': True,
                'runtime_levels': ['playbook'],
                'version': Version('3.0.2'),
            },
            # 'secureParams': {
            #     'default': True,
            #     'runtime_levels': ['organization', 'playbook'],
            # },
            'smtpSettings': {},
            'webhookResponseMarshall': {
                'runtime_levels': ['webhooktriggerservice'],
                'version': Version('4.0.0'),
            },
            'webhookServiceEndpoint': {
                'runtime_levels': ['webhooktriggerservice'],
                'version': Version('4.0.0'),
            },
            # features for TC App loop prevention
            'CreatesGroup': {
                'runtime_levels': ['playbook'],
            },
            'CreatesIndicator': {
                'runtime_levels': ['playbook'],
            },
            'CreatesSecurityLabel': {
                'runtime_levels': ['playbook'],
            },
            'CreatesTag': {
                'runtime_levels': ['playbook'],
            },
            'DeletesGroup': {
                'runtime_levels': ['playbook'],
            },
            'DeletesIndicator': {
                'runtime_levels': ['playbook'],
            },
            'DeletesSecurityLabel': {
                'runtime_levels': ['playbook'],
            },
            'DeletesTag': {
                'runtime_levels': ['playbook'],
            },
        }
        return {k: _FeatureModel(**v) for k, v in feature_data.items()}

    @property
    def updated_features(self) -> list[str]:
        """Update feature set based on App type."""
        try:
            tcex_version = Version.coerce(get_version('tcex'))
        except Exception:
            tcex_version = Version('2.0.0')

        # define deprecated features that should be removed
        deprecated_features = ['aotExecutionEnabled']

        # normalize features based on App type and TcEx version
        features = []
        for feature, model in self.known_features.items():
            if (
                model.default is True
                and (model.version is None or model.version <= tcex_version)
                and (
                    model.runtime_levels is None
                    or self.runtime_level.lower() in model.runtime_levels
                )
            ):
                features.append(feature)

        # add layoutEnabledApp if layout.json file exists in project
        if Path('layout.json').is_file():
            features.append('layoutEnabledApp')

        # extend feature list with features defined by developer
        for feature in self.features:
            model = self.known_features.get(feature)

            # exclude deprecated features
            if feature in deprecated_features:
                continue

            if model is None:
                # not sure what the feature is, but add it anyway
                features.append(feature)

                # log unknown features
                _logger.warning(f'Unknown feature found in install.json: {feature}')
            # "drop" features that should not be in the list
            elif (model.version is None or model.version <= tcex_version) and (
                model.runtime_levels is None or self.runtime_level.lower() in model.runtime_levels
            ):
                features.append(feature)

        return sorted(set(features))


class InstallJsonOrganizationModel(BaseModel):
    """Install JSON Common Model

    This model contains the common fields for the install.json file and
    the app_spec.yaml file.
    """

    feeds: list[FeedsModel] = Field(
        [],
        description='A list of features enabled for the App.',
    )
    publish_out_files: list[str] = Field(
        [],
        description=(
            'Optional field available for job-style Apps that can be scheduled to serve '
            'files. If this array is populated, the App is responsible for writing the '
            'files to the relative tc_output_path parameter that is passed in. This will '
            'enable HTTP-based file serving of these files as a unique URL available to '
            'the user in ThreatConnect. This parameter accepts an array of strings and '
            'can include file globs.'
        ),
    )
    repeating_minutes: list[int] = Field(
        [],
        description=(
            'Optional property that provides a list of minute increments to display in '
            'the Repeat Every… section in the Schedule panel of the Job Wizard. This '
            'property is relevant only for Python and Java Apps for which the developer '
            'wants to control how frequently an App can be executed. If this property is '
            'not defined, the default listing is as follows: [60, 120, 240, 360, 720].'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class InstallJsonModel(InstallJsonCommonModel, InstallJsonOrganizationModel):
    """Model definition for install.json configuration file"""

    commit_hash: str | None = Field(
        default_factory=get_commit_hash,
        description='The git commit hash from when the App was built.',
    )
    docker_image: str | None = Field(
        None,
        description='[unsupported] The docker image to run the App.',
    )
    params: list[ParamsModel] = Field(
        [],
        description='',
    )
    playbook: PlaybookModel | None = Field(
        None,
        description='',
    )
    program_icon: str | None = Field(
        None,
        description=(
            'Optional property providing the icon that will be used to represent Central '
            'Spaces Apps.'
        ),
    )
    program_name: str | None = Field(
        None,
        description='',
    )
    runtime_context: list = Field(
        [],
        description=(
            'Optional property enabling Spaces Apps to be context aware (i.e., Spaces '
            'Apps that can be added to the Details screen of an object in the '
            'ThreatConnect platform). Because this property is an array of strings, the '
            'App can be displayed in Spaces under multiple contexts within the '
            'ThreatConnect platform, including the Menu and Search screens. This property '
            'is only applicable to Spaces Apps.'
        ),
    )

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        json_encoders = json_encoders
        validate_assignment = True

    @property
    def app_output_var_type(self) -> str:
        """Return the appropriate output var type for the current App."""
        if self.is_trigger_app:
            return 'Trigger'
        return 'App'

    def filter_params(
        self,
        name: str | None = None,
        hidden: bool | None = None,
        required: bool | None = None,
        service_config: bool | None = None,
        _type: str | None = None,
        input_permutations: dict | None = None,
    ) -> dict[str, ParamsModel]:
        """Return params as name/data dict.

        Args:
            name: The name of the input to return.
            hidden: If set the inputs will be filtered based on hidden field.
            required: If set the inputs will be filtered based on required field.
            service_config: If set the inputs will be filtered based on serviceConfig field.
            _type: The type of input to return.
            input_permutations: A list of valid input names for provided permutation.

        Returns:
            dict: All valid inputs for current filter.
        """
        params = {}
        for p in self.params:
            if name is not None and p.name != name:
                continue

            if hidden is not None and p.hidden is not hidden:
                continue

            if required is not None and p.required is not required:
                continue

            if service_config is not None and p.service_config is not service_config:
                continue

            if _type is not None and p.type != _type:
                continue

            if input_permutations is not None and p.name not in input_permutations:
                continue

            params.setdefault(p.name, p)
        return params

    def get_output(self, name: str) -> OutputVariablesModel | None:
        """Return output for the matching name."""
        return self.playbook_outputs.get(name)

    def get_param(self, name: str) -> ParamsModel | None:
        """Return param for the matching name."""
        return self.params_dict.get(name)

    @property
    def optional_params(self) -> dict[str, ParamsModel]:
        """Return params as name/data model."""
        return {p.name: p for p in self.params if p.required is False}

    @property
    def package_version(self):
        """Return the major version of the App."""
        return f'v{self.program_version.major}'

    @property
    def param_names(self) -> list[str]:
        """Return the "name" field from all params."""
        return [p.name for p in self.params]

    @property
    def params_dict(self) -> dict[str, ParamsModel]:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params}

    @property
    def playbook_outputs(self) -> dict[str, OutputVariablesModel]:
        """Return outputs as name/data model."""
        return {} if self.playbook is None else {o.name: o for o in self.playbook.output_variables}

    @property
    def required_params(self) -> dict[str, ParamsModel]:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params if p.required is True}

    @property
    def service_config_params(self) -> dict[str, ParamsModel]:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params if p.service_config is True}

    @property
    def service_playbook_params(self) -> dict[str, ParamsModel]:
        """Return params as name/data dict."""
        return {p.name: p for p in self.params if p.service_config is False}
