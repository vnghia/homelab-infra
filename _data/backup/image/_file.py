import subprocess
import tempfile
from pathlib import Path


def backup(
    paths: list[Path | str],
    root_dir: Path | str,
    host: str,
    tags: list[str],
    excludes: list[str] | None = None,
):
    root_dir_path = Path(root_dir).resolve(True)

    restic_command = ["restic", "backup", "--host", host]
    for tag in tags:
        restic_command += ["--tag", tag]

    exclude_file = tempfile.NamedTemporaryFile("w", prefix="restic")
    if excludes:
        for exclude in excludes:
            exclude_file.write("{}\n".format(exclude))
        restic_command += ["--exclude-file", exclude_file.name]

    for path in paths:
        restic_command.append(Path(root_dir_path / path).resolve(True))

    print("\n\n{}\n\n".format(" ".join(restic_command)), flush=True)
    subprocess.check_call(restic_command, cwd=root_dir)


def restore(snapshot: str, host: str, tags: list[str]):
    restic_command = ["restic", "restore", snapshot, "--host", host, "--target", "/"]
    for tag in tags:
        restic_command += ["--tag", tag]

    print("\n\n{}\n\n".format(" ".join(restic_command)), flush=True)
    subprocess.check_call(restic_command)
