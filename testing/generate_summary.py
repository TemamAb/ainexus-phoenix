#!/usr/bin/env python3
"""
AI-NEXUS v5.0 - Project Summary Generator
"""

import os
from pathlib import Path
import json

def generate_project_summary():
    base_path = Path("ai-nexus-v5.0/ai-nexus-v5.0")
    
    if not base_path.exists():
        print("‚ùå Project directory not found!")
        return
    
    summary = {
        "project": "AI-NEXUS v5.0",
        "total_files": 0,
        "file_types": {},
        "modules": {},
        "largest_files": [],
        "recent_files": []
    }
    
    # Count files by type and module
    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            summary["total_files"] += 1
            
            # File type
            ext = file_path.suffix.lower()
            summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
            
            # Module
            relative_path = file_path.relative_to(base_path)
            module_parts = list(relative_path.parts)
            if len(module_parts) > 1:
                module = module_parts[0]
                summary["modules"][module] = summary["modules"].get(module, 0) + 1
            
            # File info for largest files
            try:
                size = file_path.stat().st_size
                mtime = file_path.stat().st_mtime
                
                summary["largest_files"].append({
                    "path": str(relative_path),
                    "size": size,
                    "type": ext
                })
                
                summary["recent_files"].append({
                    "path": str(relative_path),
                    "modified": mtime,
                    "type": ext
                })
            except:
                pass
    
    # Sort and limit
    summary["largest_files"] = sorted(summary["largest_files"], key=lambda x: x["size"], reverse=True)[:10]
    summary["recent_files"] = sorted(summary["recent_files"], key=lambda x: x["modified"], reverse=True)[:10]
    
    # Print summary
    print("Ì∫Ä AI-NEXUS v5.0 PROJECT SUMMARY")
    print("=" * 50)
    print(f"Ì≥Å Total Files: {summary['total_files']}")
    print(f"Ì≥ä File Types: {json.dumps(summary['file_types'], indent=2)}")
    print(f"ÌøóÔ∏è  Modules: {json.dumps(summary['modules'], indent=2)}")
    
    print("\nÌ≥à Largest Files:")
    for file in summary["largest_files"]:
        print(f"   {file['path']} - {file['size']} bytes")
    
    print("\nÌµí Recently Modified:")
    for file in summary["recent_files"]:
        print(f"   {file['path']}")
    
    # Save to file
    with open("project_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nÌ≤æ Summary saved to: project_summary.json")

if __name__ == "__main__":
    generate_project_summary()
