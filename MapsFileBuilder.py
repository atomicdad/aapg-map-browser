#!/usr/bin/env python3
"""
AAPG Map Browser – AAClient.log to maps.ini converter
Parses AAClient.log and writes a clean maps.ini for the AAPG Map Browser.
"""

import argparse
import re
from pathlib import Path
from typing import List

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Steam Workshop map names from AAClient.log to maps.ini"
    )
    parser.add_argument(
        "logfile",
        type=Path,
        help="Path to your AAClient.log file",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("maps.ini"),
        help="Output file (default: maps.ini in current folder)",
    )
    parser.add_argument(
        "--overwrite", action="store_true", default=True,
        help="Always overwrite the output file (default behavior)",
    )

    args = parser.parse_args()

    if not args.logfile.is_file():
        parser.error(f"Log file not found: {args.logfile}")

    # Regex: capture anything between the two single quotes after MapNamePart:
    pattern = re.compile(r"MapNamePart:'([^']+)'")

    maps: List[str] = []
    seen = set()

    with open(args.logfile, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "MapNamePart" in line:               # quick pre-filter
                match = pattern.search(line)
                if match:
                    name = match.group(1).strip()
                    if name and name not in seen:
                        seen.add(name)
                        maps.append(name)

    if not maps:
        print("No MapNamePart lines found in the log.")
        return

    # Write the .ini
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("[Maps]\n")
        for name in maps:
            f.write(f"{name} = 1\n")

    print(f"Done! {len(maps)} maps written to {args.output.resolve()}")

if __name__ == "__main__":
    main()