"""CLI for saving, inspecting, and compiling harness context."""
import argparse
import json
from pathlib import Path
from uuid import uuid4
from .context import ContextItem, ContextManager
from .store import JsonlMemoryStore


def main() -> None:
    parser = argparse.ArgumentParser(prog="datrixai-harness")
    parser.add_argument("--store", default=".datrixai/memory.jsonl")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="Save a durable memory or decision")
    add.add_argument("content")
    add.add_argument("--kind", default="memory")
    add.add_argument("--priority", type=int, default=50)
    add.add_argument("--pinned", action="store_true")
    listing = sub.add_parser("list", help="List saved context")
    listing.add_argument("--limit", type=int, default=100)
    comp = sub.add_parser("compile", help="Compile task context")
    comp.add_argument("--task", required=True)
    comp.add_argument("--instructions", default="")
    comp.add_argument("--max-tokens", type=int, default=4000)
    comp.add_argument("--output")
    args = parser.parse_args()
    store = JsonlMemoryStore(args.store)
    if args.command == "add":
        if not -100 <= args.priority <= 100:
            parser.error("--priority must be between -100 and 100")
        item = ContextItem(uuid4().hex[:12], args.content, args.kind, args.priority, pinned=args.pinned)
        store.add(item)
        print(json.dumps({"saved": True, "id": item.id, "store": str(store.path)}))
    elif args.command == "list":
        print(json.dumps([item.__dict__ for item in store.list(limit=args.limit)], indent=2))
    else:
        result = ContextManager(max_tokens=args.max_tokens).compile(
            store.list(), task=args.task, system_instructions=args.instructions)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(result.text, encoding="utf-8")
        print(json.dumps({"text": result.text, "selected_ids": result.selected_ids,
                          "omitted_ids": result.omitted_ids, "estimated_tokens": result.estimated_tokens,
                          "output": args.output}, indent=2))

if __name__ == "__main__":
    main()
