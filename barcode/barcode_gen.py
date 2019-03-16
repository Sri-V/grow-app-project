
import argparse


if __name__ == "__main__":
    parser  = argparse.ArgumentParser()
    parser.add_argument('prefix')
    parser.add_argument('racks')
    parser.add_argument('rows')
    parser.add_argument('trays')
    parser.add_argument('-f', '--file_name')

    args = parser.parse_args()

    if args.file_name is not None:
        filename = args.file_name
    else:
        filename = 'barcodes.txt'

    with open(filename, 'w+') as f:
        for r in range(1,int(args.racks) + 1):
            for s in range(1,int(args.rows) + 1):
                for t in range(1,int(args.trays) + 1):
                    f.write(args.prefix + str(r).zfill(3) + str(s).zfill(2) + str(t).zfill(2) + "\n")