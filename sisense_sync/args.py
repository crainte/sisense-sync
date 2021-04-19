from sisense_sync.backup import Backup
from sisense_sync.restore import Restore
from sisense_sync.remove import Remove

import argparse


parser = argparse.ArgumentParser(description='Interact with Sisense', allow_abbrev=False)
# Add subparsers to handle different arguments
subparsers = parser.add_subparsers(help="Default subcommand help", dest="action", required=True)

download   = subparsers.add_parser('download', help='Download dashboards and models')
download.add_argument('-n', '--no-commit', action='store_true', help="Skip the commit phase")
download.set_defaults(func=Backup)

upload = subparsers.add_parser('upload', help='Upload a dashboard or model')
upload.add_argument('file', help='Dashboard or DataModel to upload')
upload.add_argument('-t', '--title', dest='title', help='Update Title')
upload.add_argument('-c', '--connection', dest='connect', help='Update Connection')
upload.set_defaults(func=Restore)

remove = subparsers.add_parser('remove', help='Remove a dashboard or model')
remove.add_argument('file', help='Dashboard or DataModel to remove')
remove.set_defaults(func=Remove)

args = parser.parse_args()
