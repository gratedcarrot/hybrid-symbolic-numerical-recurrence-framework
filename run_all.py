from pathlib import Path

from src.plotting import make_plots
from src.reporting import run_all_reports


def main() -> None:
    root = Path(__file__).resolve().parent
    output_dir = root / "outputs"
    plot_dir = root / "plots"
    run_all_reports(output_dir)
    make_plots(plot_dir)
    print("Enhanced recurrence experiments completed.")
    print(f"CSV outputs saved in: {output_dir}")
    print(f"Plots saved in: {plot_dir}")


if __name__ == "__main__":
    main()
