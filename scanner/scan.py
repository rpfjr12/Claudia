# scanner/scan.py
# Async HTTP scanner for high-value programs defined in programs.json
from scanner.analysis_engine import analyze_response
import asyncio
import json
import os
import sys
from datetime import datetime

import aiohttp

# Ensure repo root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

OUTPUT_DIR = os.path.join(ROOT, "data")


async def fetch(session, url, timeout=10):
    try:
        async with session.get(url, timeout=timeout) as resp:
            text = await resp.text(errors="ignore")
            return {
                "status": resp.status,
                "url": str(resp.url),
                "headers": dict(resp.headers),
                "body_sample": text[:4096],
            }
    except Exception as e:
        return {
            "status": None,
            "url": url,
            "error": str(e),
        }


async def scan_target(session, program, target):
    """Basic HTTP probe for a single target."""
    print(f"[scanner] Probing {target}")
    result = await fetch(session, target)

    finding = {
        "program": program.get("name", "Unknown Program"),
        "program_id": program.get("id", "unknown"),
        "target": target,
        "status": result.get("status"),
        "url": result.get("url"),
        "error": result.get("error"),
        "headers": result.get("headers"),
        "body_sample": result.get("body_sample"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    return finding


async def scan_program(program, concurrency=10):
    """Scan all normalized_scope targets for a single program."""
    targets = program.get("normalized_scope", [])
    if not targets:
        print(f"[scanner] Program {program.get('name')} has no normalized_scope")
        return []

    connector = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=20)

    findings = []
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

        async def worker(t):
            async with sem:
                return await scan_target(session, program, t)

        tasks = [worker(t) for t in targets]
        for coro in asyncio.as_completed(tasks):
            finding = await coro
            findings.append(finding)

    return findings


def save_program_findings(program, findings):
    if not findings:
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date = datetime.utcnow().strftime("%Y-%m-%d")
    program_id = program.get("id", program.get("name", "unknown")).replace(" ", "_")
    filename = f"{program_id}-{date}.json"
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as fp:
        json.dump(findings, fp, indent=2)

    print(f"[scanner] Saved {len(findings)} findings for {program_id} to {path}")


async def run():
    programs_file = os.path.join(ROOT, "programs.json")
    if not os.path.exists(programs_file):
        print(f"[scanner] No programs.json at {programs_file}, exiting with 0 findings")
        return []

    with open(programs_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    programs = data.get("programs", [])
    print(f"[scanner] Loaded {len(programs)} programs")

    all_findings = []

    for program in programs:
        print(f"[scanner] Scanning program: {program.get('name')}")
        findings = await scan_program(program)
        save_program_findings(program, findings)
        all_findings.extend(findings)

    # Also write a global combined file for your aggregator/pipeline
    combined_path = os.path.join(OUTPUT_DIR, "scan_results.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_findings, f, indent=2)

    print(f"[scanner] Wrote {len(all_findings)} total findings to {combined_path}")
    return all_findings


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
