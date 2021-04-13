import argparse

parser = argparse.ArgumentParser(description='Upload documents to sisense', allow_abbrev=False)
parser.add_argument('file', help='Dashboard or DataModel to upload')
parser.add_argument('-t', '--title', dest='title', help='Update Title')
parser.add_argument('-c', '--connection', dest='connect', help='Update Connection')

args = parser.parse_args()
