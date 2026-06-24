import subprocess
import sys


PIPELINE_STEPS = [
    (
        "Load raw readings into SQLite",
        [sys.executable, "-m", "netwatch.pipeline.load_to_sqlite"],
    ),
    (
        "Run data quality checks",
        [sys.executable, "-m", "netwatch.pipeline.data_quality_checks"],
    ),
    (
        "Detect anomaly readings",
        [sys.executable, "-m", "netwatch.analytics.anomaly_detection"],
    ),
    (
        "Build node summary",
        [sys.executable, "-m", "netwatch.analytics.build_node_summary"],
    ),
    (
        "Query reporting views",
        [sys.executable, "-m", "netwatch.reporting.query_raw_data"],
    ),
    (
        "Generate visualization charts",
        [sys.executable, "-m", "netwatch.visualization.utilization_charts"],
    ),
]


def run_pipeline_step(step_name, pipeline_command):
    print(f"\n=== {step_name} ===", flush=True)

    completed_process = subprocess.run(pipeline_command)

    if completed_process.returncode != 0:
        print(f"\nPipeline failed during step: {step_name}", flush=True)
        raise SystemExit(completed_process.returncode)


def main():
    print("Starting NetWatch pipeline", flush=True)

    for step_name, pipeline_command in PIPELINE_STEPS:
        run_pipeline_step(step_name, pipeline_command)

    print("\nNetWatch pipeline completed successfully", flush=True)


if __name__ == "__main__":
    main()
