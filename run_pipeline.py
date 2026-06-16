import subprocess


PIPELINE_STEPS = [
    ("Load raw readings into SQLite", ["python", "load_to_sqlite.py"]),
    ("Run data quality checks", ["python", "data_quality_checks.py"]),
    ("Build node summary", ["python", "build_node_summary.py"]),
    ("Query reporting views", ["python", "query_raw_data.py"]),
]


def run_pipeline_step(step_name, pipeline_command):
    print(f"\n=== {step_name} ===")

    completed_process = subprocess.run(pipeline_command)

    if completed_process.returncode != 0:
        print(f"\nPipeline failed during step: {step_name}")
        raise SystemExit(completed_process.returncode)


def main():
    print("Starting NetWatch pipeline")

    for step_name, pipeline_command in PIPELINE_STEPS:
        run_pipeline_step(step_name, pipeline_command)

    print("\nNetWatch pipeline completed successfully")


if __name__ == "__main__":
    main()
