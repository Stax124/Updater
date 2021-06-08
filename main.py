import argparse
import updater

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generate", action="store_true")
parser.add_argument("-e", "--exclude", type=str)
parser.add_argument("-d", "--directory", type=str, default=".")
parser.add_argument("-r", "--reset", action="store_true")
parser.add_argument("hashtable", type=str, help="URL or path to hashtable")
args = parser.parse_args()

args.exclude = args.exclude.split(",") if args.exclude != None else []

main_updater = updater.Updater(args.directory)

if args.generate:
    main_updater.dump_hashtable(args.hashtable, exclude=args.exclude)
else:
    print(main_updater.compare(mode=updater.Mode.URL, target=args.hashtable, rebase=args.rebase))
    # main_updater.download("http://localhost",
    #       updater.Mode.URL, args.hashtable)
