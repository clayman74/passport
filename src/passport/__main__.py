import asyncio
from pathlib import Path

import click
import uvloop  # type: ignore
from aiohttp_micro.management.server import server  # type: ignore
from aiohttp_storage.management.storage import storage  # type: ignore
from config import (  # type: ignore
    ConsulConfig,
    EnvValueProvider,
    FileValueProvider,
    load,
)

from passport.app import AppConfig, init


@click.group()
@click.option("--conf-dir", default=None)
@click.option("--debug", default=False, is_flag=True)
@click.pass_context
def cli(ctx, conf_dir: str = None, debug: bool = False) -> None:
    uvloop.install()
    loop = asyncio.get_event_loop()

    if conf_dir:
        conf_path = Path(conf_dir)
    else:
        conf_path = Path.cwd()

    consul_config = ConsulConfig()
    load(consul_config, providers=[EnvValueProvider()])

    config = AppConfig(
        defaults={
            "consul": consul_config,
            "debug": debug,
            "db": {
                "user": "passport",
                "password": "passport",
                "database": "passport",
            },
        }
    )
    load(config, providers=[FileValueProvider(conf_path), EnvValueProvider()])

    app = loop.run_until_complete(init("passport", config))

    ctx.obj["app"] = app
    ctx.obj["config"] = config
    ctx.obj["loop"] = loop


cli.add_command(server, name="server")
cli.add_command(storage, name="storage")


if __name__ == "__main__":
    cli(obj={})
