import yaml
import os, sys
import pathlib
import logging

kwargs = None
experiment_filters = {}

def store_kwargs(_kwargs, *, execution_mode):
    global kwargs
    kwargs = _kwargs
    kwargs["execution_mode"] = execution_mode


def get_benchmark_yaml_file(benchmark_file):
    if not benchmark_file:
        benchmark_file = os.environ.get("MATBENCH_BENCHMARK_FILE")

    if not benchmark_file:
        raise ValueError("benchmark_file must be passed in the command-line or with the MATBENCH_BENCHMARK_FILE environment variable.")

    benchmark_file_path = pathlib.Path(os.path.realpath(benchmark_file))

    if not benchmark_file_path.exists():
        raise FileNotFoundError(f"'{benchmark_file}' does not exit.")
    if not benchmark_file_path.is_file():
        raise FileNotFoundError(f"'{benchmark_file}' must be a file.")

    # parse the benchmark file YAML
    logging.info(f"Loading the benchmark file {benchmark_file} ...")
    with open(benchmark_file_path) as f:
        benchmark_yaml_file = yaml.safe_load(f)

    return benchmark_yaml_file


def update_env_with_env_files():
    """
    Overrides the function default args with the flags found in the environment variables files
    """
    for env in ".env", ".env.generated":
        try:
            with open(env) as f:
                for line in f.readlines():
                    key, found , value = line.strip().partition("=")
                    if not found:
                        logging.warning("invalid line in {env}: {line.strip()}")
                        continue
                    if key in os.environ: continue # prefer env to env file
                    os.environ[key] = value
        except FileNotFoundError: pass # ignore missing files


def update_kwargs_with_env(kwargs):
    # override the function default args with the flags found in the environment variables

    for flag, current_value in kwargs.items():
        if current_value: continue # already set, ignore.

        env_value = os.environ.get(f"MATBENCH_{flag.upper()}")
        if not env_value: continue # not set, ignore.
        kwargs[flag] = env_value # override the function arg with the environment variable value


def update_kwargs_with_benchmark_file(kwargs, benchmark_desc_file):
    # override the function default args with the flags found in the benchmark file
    for flag, current_value in kwargs.items():
        if current_value: continue # already set, ignore.

        for item_name in (f"--{flag.replace('_', '-')}", f"--{flag}"):
            file_value = benchmark_desc_file.get(item_name)
            if file_value is None: continue # not set, ignore.
            kwargs[flag] = file_value # override the function arg with the benchmark file value

            del benchmark_desc_file[item_name]
            break

    # warn for every flag remaining in the benchmark file
    for key, value in benchmark_desc_file.items():
        if not key.startswith("--"): continue

        logging.warning(f"unexpected flag found in the benchmark file: {key} = '{value}'")


def check_mandatory_kwargs(kwargs, mandatory_flags):
    err = False
    for flag in mandatory_flags:
        if kwargs.get(flag): continue

        logging.error(f"--{flag} must be set in CLI, in the benchmark file or though MATBENCH_{flag.upper()} environment variable.")
        err = True

    if err:
        print(kwargs)
        raise SystemExit(1)


def goto_work_directory(kwargs):
    work_dir = kwargs["work_dir"]
    if not work_dir:
        work_dir = os.environ["MATBENCH_WORK_DIR"]
    if not work_dir:
        return

    os.chdir(work_dir)


def setup_env_and_kwargs(kwargs):
    # overriding order: env file <- env var <- benchmark file <- cli
    goto_work_directory(kwargs)
    update_env_with_env_files()
    update_kwargs_with_env(kwargs)

    filters = kwargs.get("filters")
    if isinstance(filters, bool):
        filters = str(filters)

    if filters:
        parse_filters(filters)

def parse_filters(filters):
    for kv in filters.split(","):
        key, found, value = kv.partition("=")
        if not found:
            logging.error(f"Unexpected filter value: {kv}")
            sys.exit(1)

        if ":" in value:
            value = value.split(":")

        experiment_filters[key] = value

class TaskRunner:
    """
    TaskRunner

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    If you're seeing this text, put the --help flag earlier in your list
    of command-line arguments, this is a limitation of the CLI parsing library
    used by the MatrixBenchmarking.
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    """
    def __init__(self, run):
        self.run = run

    def __str__(self): return "---"
