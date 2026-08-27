import argparse
import sys

from turtle_soup.catalog.importer import PuzzleCatalogError, import_puzzle_catalog


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m turtle_soup.catalog")
    parser.add_argument("--catalog-path", required=True)
    parser.add_argument("--database-path", required=True)
    args = parser.parse_args(argv)
    try:
        import_puzzle_catalog(
            catalog_path=args.catalog_path,
            database_path=args.database_path,
        )
    except PuzzleCatalogError as exc:
        print(f"puzzle catalog import failed: {exc}", file=sys.stderr)
        return 1
    print("puzzle catalog import completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
