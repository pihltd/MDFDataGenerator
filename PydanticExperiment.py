import bento_mdf
import pydantic
import argparse
from crdclib import crdclib


def main(args):
    configs = crdclib.readYAML(args.configfile)
    input_mdf = bento_mdf.MDF(*configs['mdffiles'])
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", help="Verbose Output")

    args = parser.parse_args()

    main(args)