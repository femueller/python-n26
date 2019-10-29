from container_app_conf import ConfigBase
from container_app_conf.entry.file import FileConfigEntry
from container_app_conf.entry.string import StringConfigEntry
from container_app_conf.source.env_source import EnvSource
from container_app_conf.source.toml_source import TomlSource
from container_app_conf.source.yaml_source import YamlSource

NODE_ROOT = "n26"

MFA_TYPE_APP = "app"
MFA_TYPE_SMS = "sms"


class Config(ConfigBase):

    def __new__(cls, *args, **kwargs):
        if "data_sources" not in kwargs.keys():
            yaml_source = YamlSource("n26")
            toml_source = TomlSource("n26")
            data_sources = [
                EnvSource(),
                yaml_source,
                toml_source
            ]
            kwargs["data_sources"] = data_sources

        if "write_reference" not in kwargs.keys():
            kwargs["write_reference"] = False

        return super(Config, cls).__new__(cls, *args, **kwargs)

    USERNAME = StringConfigEntry(
        description="N26 account username",
        example="john.doe@example.com",
        key_path=[
            NODE_ROOT,
            "username"
        ],
        required=True
    )

    PASSWORD = StringConfigEntry(
        description="N26 account password",
        example="$upersecret",
        key_path=[
            NODE_ROOT,
            "password"
        ],
        required=True,
        secret=True
    )

    LOGIN_DATA_STORE_PATH = FileConfigEntry(
        description="File path to store login data",
        example="~/.config/n26/token_data",
        key_path=[
            NODE_ROOT,
            "login_data_store_path"
        ],
        required=False,
        default=None
    )

    MFA_TYPE = StringConfigEntry(
        description="Multi-Factor-Authentication type to use",
        example=MFA_TYPE_APP,
        key_path=[
            NODE_ROOT,
            "mfa_type"
        ],
        regex="^({})$".format("|".join([MFA_TYPE_APP, MFA_TYPE_SMS])),
        default=MFA_TYPE_APP
    )
