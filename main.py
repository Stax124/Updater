import argparse
import updater

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generate", action="store_true",
                    help="Generate hashtable")
parser.add_argument("-e", "--exclude", type=str,
                    help="Exclude directories or files (separated by comma (','))")
parser.add_argument("-v", "--verify", action="store_true",
                    help="Don't download the files, just verify integrity")
parser.add_argument("-y", "--yes", action="store_true",
                    help="Say yes to any prompt")
parser.add_argument("-m", "--mirror", type=str,
                    help="URL, that will be used as root for downloading")
parser.add_argument("-c", "--no-changed", action="store_true",
                    help="Suppress outputting list of differences")
parser.add_argument("-a", "--all", action="store_true",
                    help="Hash all files, not only those present in remote hashtable")
parser.add_argument("hashtable", type=str, help="URL or path to hashtable")
args = parser.parse_args()

args.exclude = args.exclude.split(",") if args.exclude != None else []
args.yes = not args.yes

main_updater = updater.Updater()

if args.generate:
    main_updater.dump_hashtable(args.hashtable, args.exclude)
elif args.verify:
    changed, size = main_updater.compare(args.hashtable, args.hash_all)
    changed = list(changed)
    changed.sort()

    if not args.no_changed:
        for item in changed:
            print(item)

    print("Total size: "+main_updater.human_readable(size))
else:
    main_updater.download(args.mirror, args.hashtable, args.yes, args.hash_all)
