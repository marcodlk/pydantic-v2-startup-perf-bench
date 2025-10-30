import argparse
from collections.abc import Sequence
from pathlib import Path

import nox
import nox.command

__DIR__ = Path(__file__).parent

nox.options.sessions = ["test"]

BENCHMARK_REPEAT = 20


@nox.session(venv_backend="uv")
@nox.parametrize("pydantic", ["1.10.18", "2.12.3"], ids=["pydantic-v1", "pydantic-v2"])
def test(session: nox.Session, pydantic: str):
    session.run_install(
        "uv", "sync", "--frozen", env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    )
    session.install(f"pydantic=={pydantic}")
    session.run("pytest", "-svv")


@nox.session(venv_backend="uv")
@nox.parametrize(
    "pydantic",
    [
        "1.10.18",
        # "2.6.3",
        "2.7.2",
        "2.8.2",
        "2.9.2",
        "2.10.2",
        "2.11.0a1",
        "2.11.0b1",
        "2.12.0",
        "2.12.1",
        "2.12.2",
        "2.12.3",
    ],
    ids=[
        "pydantic-v1",
        # "pydantic-v2.6",
        "pydantic-v2.7",
        "pydantic-v2.8",
        "pydantic-v2.9",
        "pydantic-v2.10",
        "pydantic-v2.11a",
        "pydantic-v2.11b",
        "pydantic-v2.12.0",
        "pydantic-v2.12.1",
        "pydantic-v2.12.2",
        "pydantic-v2.12.3",
    ],
)
def benchmark(session: nox.Session, pydantic: str):
    args = _parse_benchmark_args(session.posargs)
    repeat: int = args.repeat
    results_file = args.results_file

    extra_args = (f"--results-file={results_file}",) if results_file else ()

    session.run_install(
        "uv", "sync", "--frozen", env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location}
    )
    session.install(f"pydantic=={pydantic}")

    bench_arg_combos = (
        [],
        ["--strict-models"],
        ["--defer-build"],
        ["--strict-models", "--defer-build"],
    )
    for bench_args in bench_arg_combos:
        session.run("python", "bench/run.py", "--no-save")  # Warmup
        for _ in range(repeat):
            session.run("python", "bench/run.py", *bench_args, *extra_args)

    # Generate plot of results
    session.run("python", "bench/plot.py", *extra_args)


def _parse_benchmark_args(args: Sequence[str]):
    parser = argparse.ArgumentParser(prog="nox -s benchmark")
    parser.add_argument(
        "--repeat", type=int, default=BENCHMARK_REPEAT, help="Number of repetitions"
    )
    parser.add_argument("--results-file", type=str, default=None, help="Results file path")
    return parser.parse_args(args)


@nox.session(python=False)
def format(session: nox.Session):  # noqa: A001
    session.run("ruff", "check", "--fix")
    session.run("ruff", "format")


@nox.session(python=False)
def lint(session: nox.Session):
    session.run("ruff", "check", "--no-fix")
    session.run("ruff", "format", "--check")
