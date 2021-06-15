import argparse
import updater

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--generate", action="store_true")
parser.add_argument("-e", "--exclude", type=str)
parser.add_argument("-d", "--directory", type=str, default=".")
parser.add_argument("-v", "--verify", action="store_true")
parser.add_argument("-y", "--yes", action="store_true")
parser.add_argument("-m", "--mirror", type=str)
parser.add_argument("hashtable", type=str, help="URL or path to hashtable")
args = parser.parse_args()

args.exclude = args.exclude.split(",") if args.exclude != None else []
args.yes = not args.yes

main_updater = updater.Updater(args.directory)

if args.generate:
    main_updater.dump_hashtable(args.hashtable, args.exclude)
elif args.verify:
    changed, size = main_updater.compare(args.hashtable)
    changed = list(changed)
    changed.sort()
    
    for item in changed:
        print(item)
        
    print("Total size: "+main_updater.human_readable(size))
else:
    main_updater.download(args.mirror, args.hashtable, args.yes)
