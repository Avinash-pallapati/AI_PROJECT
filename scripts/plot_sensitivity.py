#!/usr/bin/env python3
"""
Generate publication-quality SVG and text plots from sensitivity results CSV.
Requires zero external dependencies (pure Python).
"""

import os
import csv
import json

def generate_svg_bar_chart(data, x_key, y_key, title, y_label, output_file, sort_by_y=False):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    if sort_by_y:
        data = sorted(data, key=lambda x: float(x[y_key]))
    
    width = 750
    height = 420
    margin_left = 80
    margin_right = 40
    margin_top = 60
    margin_bottom = 70
    
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    
    max_val = max(float(d[y_key]) for d in data) * 1.15
    max_val = max(max_val, 1.0)
    
    bar_width = plot_width / (len(data) * 1.5)
    bar_spacing = plot_width / len(data)
    
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <rect width="100%" height="100%" fill="#ffffff" />',
        f'  <text x="{width/2}" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#1e293b">{title}</text>',
        f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#64748b" stroke-width="2" />',
        f'  <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{width - margin_right}" y2="{margin_top + plot_height}" stroke="#64748b" stroke-width="2" />'
    ]
    
    # Grid lines and Y-axis labels
    num_y_ticks = 5
    for i in range(num_y_ticks + 1):
        y_val = (max_val / num_y_ticks) * i
        y_pos = margin_top + plot_height - (i / num_y_ticks) * plot_height
        svg.append(f'  <line x1="{margin_left}" y1="{y_pos}" x2="{width - margin_right}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4" />')
        svg.append(f'  <text x="{margin_left - 12}" y="{y_pos + 4}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#475569">{y_val:.1f}%</text>')
        
    svg.append(f'  <text x="25" y="{margin_top + plot_height/2}" text-anchor="middle" transform="rotate(-90, 25, {margin_top + plot_height/2})" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#334155">{y_label}</text>')
    
    # Bars
    for idx, d in enumerate(data):
        val = float(d[y_key])
        bar_h = (val / max_val) * plot_height
        x_pos = margin_left + idx * bar_spacing + (bar_spacing - bar_width) / 2
        y_pos = margin_top + plot_height - bar_h
        
        # Color coding: red for sensitive (>1.0%), blue/green for robust
        if val > 3.0:
            fill_color = "#ef4444"
        elif val > 0.5:
            fill_color = "#f59e0b"
        else:
            fill_color = "#10b981"
            
        svg.append(f'  <rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_h}" fill="{fill_color}" rx="4" />')
        svg.append(f'  <text x="{x_pos + bar_width/2}" y="{y_pos - 6}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="{fill_color}">{val:.2f}%</text>')
        label = d[x_key]
        svg.append(f'  <text x="{x_pos + bar_width/2}" y="{margin_top + plot_height + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="500" fill="#1e293b">{label}</text>')
        
    svg.append('</svg>')
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated SVG: {output_file}")


def main():
    csv_file = "./results/sensitivity/sensitivity_results.csv"
    if not os.path.exists(csv_file):
        print(f"CSV not found: {csv_file}")
        return
        
    data = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
            
    out_dir = "./results/sensitivity/plots"
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Layer vs accuracy-drop plot (sequential layer order)
    generate_svg_bar_chart(
        data=data,
        x_key="layer",
        y_key="accuracy_drop",
        title="Layer-by-Layer Accuracy Degradation (INT8 → INT4)",
        y_label="Top-1 Accuracy Drop (percentage points)",
        output_file=os.path.join(out_dir, "layer_vs_drop.svg"),
        sort_by_y=False
    )
    
    # 2. Sorted sensitivity plot (least sensitive to most sensitive)
    generate_svg_bar_chart(
        data=data,
        x_key="layer",
        y_key="accuracy_drop",
        title="Sorted Layer Sensitivity (Least Sensitive to Most Sensitive)",
        y_label="Top-1 Accuracy Drop (percentage points)",
        output_file=os.path.join(out_dir, "sorted_sensitivity.svg"),
        sort_by_y=True
    )

if __name__ == "__main__":
    main()
