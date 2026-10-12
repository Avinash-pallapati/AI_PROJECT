"""
Visualize search convergence, Pareto frontiers, and resource reductions.
Zero-dependency SVG generator.
"""

import os
import csv
from typing import List, Dict, Any


def render_search_progression_svg(history_csv: str, output_path: str):
    if not os.path.exists(history_csv):
        return

    records = []
    with open(history_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["accepted_rejected"] == "ACCEPTED":
                records.append(r)

    if not records:
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width = 700
    height = 360
    margin = 60

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <rect width="100%" height="100%" fill="#ffffff" />',
        f'  <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1e293b">Search Convergence: Accuracy vs BRAM Allocation</text>',
        f'  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#64748b" stroke-width="2" />',
        f'  <line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#64748b" stroke-width="2" />',
        f'  <text x="{margin}" y="{height - margin + 30}" font-family="Arial, sans-serif" font-size="12" fill="#475569">Baseline (INT8)</text>',
        f'  <text x="{width - margin}" y="{height - margin + 30}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#475569">Final Iteration</text>'
    ]

    # Plot steps
    num_steps = len(records)
    step_width = (width - 2 * margin) / max(num_steps - 1, 1)

    points_acc = []
    points_bram = []

    for i, rec in enumerate(records):
        x = margin + i * step_width
        acc = float(rec["accuracy"])
        bram = float(rec["BRAM"])

        # Normalize y
        y_acc = height - margin - ((acc - 80.0) / 5.0) * (height - 2 * margin)
        y_bram = height - margin - ((bram - 100.0) / 100.0) * (height - 2 * margin)

        points_acc.append((x, y_acc, acc))
        points_bram.append((x, y_bram, bram))

    # Connect lines
    path_acc = " ".join([f"{'M' if i==0 else 'L'} {p[0]} {p[1]}" for i, p in enumerate(points_acc)])
    path_bram = " ".join([f"{'M' if i==0 else 'L'} {p[0]} {p[1]}" for i, p in enumerate(points_bram)])

    svg.append(f'  <path d="{path_acc}" fill="none" stroke="#2563eb" stroke-width="3" />')
    svg.append(f'  <path d="{path_bram}" fill="none" stroke="#10b981" stroke-width="3" stroke-dasharray="4" />')

    for p in points_acc:
        svg.append(f'  <circle cx="{p[0]}" cy="{p[1]}" r="4" fill="#2563eb" />')
    for p in points_bram:
        svg.append(f'  <circle cx="{p[0]}" cy="{p[1]}" r="4" fill="#10b981" />')

    # Legend
    svg.append(f'  <line x1="{width - 200}" y1="50" x2="{width - 170}" y2="50" stroke="#2563eb" stroke-width="3" />')
    svg.append(f'  <text x="{width - 160}" y="54" font-family="Arial, sans-serif" font-size="12" fill="#1e293b">Accuracy (%)</text>')
    svg.append(f'  <line x1="{width - 200}" y1="70" x2="{width - 170}" y2="70" stroke="#10b981" stroke-width="3" stroke-dasharray="4" />')
    svg.append(f'  <text x="{width - 160}" y="74" font-family="Arial, sans-serif" font-size="12" fill="#1e293b">BRAM Blocks</text>')

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Rendered search convergence plot: {output_path}")
