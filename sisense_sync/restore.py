from sisense_sync.client import client
from loguru import logger
from pathlib import Path
from PySense import PySenseDataModel

import os
import json


class Restore:

    def __init__(self, args):
        self.client = client
        self.version = client.param_dict['version']
        self.__handle_args(args)

    def __handle_args(self, arg):
        self.new = arg.new
        if arg.connect:
            try:
                with open(arg.file, 'r+') as f:
                    data = json.load(f)
                    f.seek(0)
                    if arg.connect:
                        logger.info("Updating connection parameters")
                        for dataset in data['datasets']:
                            logger.opt(colors=True).info(f"Replacing connection string: <blue>{dataset['connection']['parameters']}</blue>")
                            dataset['connection']['parameters'] = arg.connect
                    json.dump(data, f, indent=4)
                    f.truncate()
            except Exception as e:
                logger.exception(f"Failed to update {arg.file}, Reason: {e}")
                raise

        if arg.file.endswith('.dash'):
            self.__upload_dashboard(arg.file)
        elif arg.file.endswith('.smodel'):
            self.__upload_model(arg.file)
        else:
            raise TypeError('Expected .dash or .smodel')

    def __upload_dashboard(self, file):
        try:
            # path, action='overwrite', republish=True
            ret = self.client.import_dashboards(file)[0]
            logger.success(f"Dashboard {ret.get_oid()} uploaded. Title: '{ret.get_title()}'")
        except Exception as e:
            logger.exception(f"Failed to upload dashboard, Reason: {e}")
            raise

    def __upload_model(self, file):

        if self.version.lower() != 'linux':
            logger.error(f"{self.version} does not support model uploads. Please use Linux as the version.")
            exit(1)

        try:
            # Fake the target object
            fake = dict()
            fake['oid'] = Path(file).stem
            target = PySenseDataModel.DataModel(self.client, fake)

            if self.new:
                ret = self.client.import_schema(file)
                logger.success(f"Model {ret.get_oid()} uploaded. Title: '{ret.get_title()}'")
            else:
                # update an existing model
                ret = self.client.import_schema(file, target_data_model=target)
                logger.success(f"Model {ret.get_oid()} uploaded. Title: '{ret.get_title()}'")
        except Exception as e:
            logger.exception(f"Failed to upload model, Reason: {e}")
            raise
