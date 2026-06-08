import argparse
import sys
from pathlib import Path

from .schema import C1Result
from .graphviz_builder import build_dot
from .renderer import render_dot_to_files
from .html_report import write_html_report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pyscope.visualizer")
    parser.add_argument("--input-json", required=True, help="Path to C1 JSON input")
    parser.add_argument("--output-dir", required=True, help="Directory to write outputs")
    args = parser.parse_args(argv)

    input_path = Path(args.input_json)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        print(f"Input JSON not found: {input_path}", file=sys.stderr)
        return 2

    model = C1Result.from_json(str(input_path))
    dot = build_dot(model)
    artifacts = render_dot_to_files(dot, str(output_dir))
    html = write_html_report(str(output_dir), artifacts, model.metrics)

    print("Artifacts:")
    for key, value in artifacts.items():
        print(f" - {key}: {value}")
    print(f" - html: {html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
