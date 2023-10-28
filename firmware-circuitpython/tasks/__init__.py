import ast
import pathlib
import time
from invoke.tasks import task
import json
import requests

CIRCUITPY_HOSTNAME = ""
CIRCUITPY_WEB_API_PASSWORD = ""


def select_host(c, host="") -> str:
    if host:
        return host
    elif CIRCUITPY_HOSTNAME:
        return CIRCUITPY_HOSTNAME
    elif c.config.circuitpy_hostname:
        return c.config.circuitpy_hostname
    raise Exception("hostname is not set")


def select_pass(c) -> str:
    return (
        CIRCUITPY_WEB_API_PASSWORD
        if CIRCUITPY_WEB_API_PASSWORD
        else c.config.circuitpy_web_api_password
    )


@task()
def upload(c, src="main.py", host="", dst="", code=False):
    host = select_host(c, host)
    password = select_pass(c)

    if dst == "":
        if src == "_code.py" or code:
            dst = "code.py"
        else:
            dst = src

    cmd = (
        f"curl -v -u :{password} -T {src} -L --location-trusted http://{host}/fs/{dst}"
    )

    print(cmd.replace(password, "********"))

    c.run(cmd)


@task()
def mkdir(
    c,
    directory,
    host="",
):
    host = select_host(c, host)
    password = select_pass(c)

    cmd = f"curl -XPUT -v -u :{password} -L --location-trusted http://{host}/fs/{directory}"

    print(cmd.replace(password, "********"))

    c.run(cmd)


@task()
def upload_libs(c, path="lib", host=""):
    upload(
        c, src="imports/micropython-typing-dummy/typing.py", dst="typing.py", host=host
    )

    for item in pathlib.Path(path).iterdir():
        print(item.as_posix())
        if item.is_dir():
            mkdir(c, f"{item}/", host=host)
            upload_libs(c, path=str(item), host=host)
            continue
        if item.is_file() and item.suffix in (".mpy", ".py"):
            upload(c, src=item.as_posix(), host=host)


@task
def upload_codes(c, host=""):
    for item in pathlib.Path("./").iterdir():
        if item.is_file() and not item.is_symlink() and item.suffix == ".py":
            upload(c, src=item.as_posix(), host=host)


@task
def upload_config(c, host=""):
    mkdir(c, f"config/", host=host)
    for item in pathlib.Path("./config").iterdir():
        if item.is_file() and not item.is_symlink() and item.suffix == ".py":
            upload(c, src=item.as_posix(), host=host)
