from pathlib import Path

from dynaconf import Dynaconf

root_path = Path(__file__).parent.parent.parent

settings = Dynaconf(
    environments=True,
    envvar_prefix="AUTH",
    settings_files=[root_path / "settings.toml", root_path / "secrets.toml"],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
