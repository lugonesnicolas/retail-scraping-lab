import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from retail_scraping_lab.models.product import Product

ExportFormat = Literal["json", "csv"]


def export_products(
    products: list[Product],
    output_dir: Path,
    export_format: ExportFormat = "json",
    *,
    filename_stem: str | None = None,
) -> Path:
    """Exporta una lista de productos validados a JSON o CSV en output_dir.

    Devuelve la ruta del archivo generado. No hace scraping ni parsing: recibe
    productos ya validados por models.product.Product. Sin `filename_stem`, el
    nombre lleva el timestamp de la exportacion; con un stem fijo, volver a
    exportar sobrescribe el mismo archivo.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = filename_stem or f"products_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    output_path = output_dir / f"{stem}.{export_format}"

    if export_format == "json":
        payload = [product.model_dump(mode="json") for product in products]
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        rows = [product.model_dump(mode="json") for product in products]
        fieldnames = list(rows[0].keys()) if rows else []
        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return output_path
