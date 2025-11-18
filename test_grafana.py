#!/usr/bin/env python3
# Quick test of the Grafana layout
from start_engine import GrafanaStartEngine

engine = GrafanaStartEngine()
engine.display_grafana_header()
engine.display_2x3_grid() 
engine.display_system_metrics()
