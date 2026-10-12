from __future__ import annotations

from backend.data_loader import save_synthetic_dataset


if __name__ == "__main__":
    output_path = "backend/data/synthetic/retail_sales_opportunities.csv"
    save_synthetic_dataset(output_path=output_path, n_rows=2500, random_state=42)
    print(f"Synthetic dataset written to {output_path}")
