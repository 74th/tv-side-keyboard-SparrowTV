import pathlib
import getpass
from invoke import task

@task
def mount(c):
    uid = c.run("id -u", echo=False).stdout.strip()
    gid = c.run("id -g", echo=False).stdout.strip()
    p = pathlib.Path("/media/CIRCUITPY")
    if not p.exists():
        c.run(f"sudo mkdir {p}")
    if len(list(p.glob("*"))) == 0:
        c.run(f"sudo mount /dev/sda1 {p} -o uid={uid},gid={gid}")

@task
def upload_code(c):
    c.run("cp main.py /media/CIRCUITPY/code.py")
    c.run("sync")

@task
def umount(c):
    c.run(f"sudo umount /dev/sda1")

@task
def upload(c):
    mount(c)
    upload_code(c)
    umount(c)
