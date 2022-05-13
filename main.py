import argparse
import logging as console
import re

import coloredlogs
import rich.traceback

import updater

# Apply rich tracebacks
rich.traceback.install()

# Set up parsing of command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generate", action="store_true",
                    help="Generate hashtable of current directory (recursive)")
parser.add_argument("-e", "--exclude", type=str,
                    help="Exclude directories or files separated by comma (',') (buidl,dist,venv,__pycache__)")
parser.add_argument("--verify", action="store_true",
                    help="Don't download the files, just verify integrity")
parser.add_argument("-y", "--yes", action="store_true",
                    help="Say yes to any prompt")
parser.add_argument("-m", "--mirror", type=str,
                    help="URL, that will be used as root for downloading")
parser.add_argument("-c", "--no-changed", action="store_true",
                    help="Suppress outputting list of differences")
parser.add_argument("-a", "--hash_all", action="store_true",
                    help="Hash all files, not only those present in remote hashtable")
parser.add_argument("-d", "--destination", type=str,
                    default=".", help="Destination directory")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Verbose output", default=False)
parser.add_argument("-r", "--reset", action="store_true", default=False,
                    help="Overwrite any changes made to the files, reset everything to the remote state")
parser.add_argument("hashtable", type=str, help="URL or path to hashtable")
args = parser.parse_args()

# Change logging level to DEBUG if verbose is set


if args.verbose:
    # Apply colored logs
    coloredlogs.install(
        level='DEBUG', fmt='%(levelname)s | %(asctime)s | %(message)s', datefmt=r"%H:%M:%S"
    )
else:
    # Apply colored logs
    coloredlogs.install(
        level='INFO', fmt='%(levelname)s | %(asctime)s | %(message)s', datefmt=r"%H:%M:%S"
    )

# Correct exclude list if it is set
args.exclude = args.exclude.split(",") if args.exclude != None else []
console.debug(f"Parsed exclude: {args.exclude}")

args.yes = not args.yes

main_updater = updater.Updater(args.destination)

if args.generate:
    # Generate hashtable and exit

    console.debug("Generating hashtable")
    main_updater.dump_hashtable(args.hashtable, args.exclude)
    console.info("Hashtable generated")
elif args.verify:
    # Verify local files based on remote, output difference and exit

    console.debug("Verifying...")
    changed, size = main_updater.compare(args.hashtable)
    changed = list(changed)  # type: ignore
    changed.sort()  # type: ignore

    print("---Changed or missing files---")
    for item in changed:
        print(item)

    print("Total size: " + main_updater.human_readable(size))
else:
    if not args.mirror:
        # strip the last part of url
        pattern = re.compile(r"(.*/)")
        args.mirror = pattern.search(args.hashtable).group(1)  # type: ignore

        console.info(f"Using mirror: {args.mirror}")

        # We need slash at the end of mirror for correct URIs
        if not args.mirror[-1] == "/":
            args.mirror += "/"

    console.debug("Downloading hashtable...")
    main_updater.run(args.mirror, args.hashtable, args.yes, args.reset)
