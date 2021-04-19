from sisense_sync.client import client
from loguru import logger
from pathlib import Path
from PySense import PySenseDataModel
from PySense import PySenseDashboard
from PySense.PySenseException import PySenseException

import os
import json


class Remove:

    def __init__(self, args):
        self.client = client
        self.version = client.param_dict['version']
        self.__handle_args(args)

    def __handle_args(self, arg):
        if arg.file.endswith('.dash'):
            self.__remove_dashboard(arg.file)
        elif arg.file.endswith('.smodel'):
            self.__remove_model(arg.file)
        else:
            raise TypeError('Expected .dash or .smodel')

    def __fake_it(self, file):
        fake = dict()
        fake['oid'] = Path(file).stem
        return fake

    def __remove_dashboard(self, file):
        try:
            target = PySenseDashboard.Dashboard(self.client, self.__fake_it(file))
            # does not return
            self.client.delete_dashboards(target)
            logger.success(f"Dashboard {target.get_oid()} deleted")
        except PySenseException as e:
            logger.error(e)
            # not sure if need to raise here
        except Exception as e:
            logger.exception(f"Failed to delete dashboard, Reason: {e}")
            raise

    def __remove_model(self, file):

        if self.version.lower() != 'linux':
            logger.error(f"{self.version} does not support model deletes. Please use Linux as the version.")
            exit(1)

        try:
            target = PySenseDataModel.DataModel(self.client, self.__fake_it(file))
            # does not return
            self.client.delete_data_models(target)
            logger.success(f"Model {target.get_oid()} deleted")
        except PySenseException as e:
            logger.error(e)
            # not sure if need to raise here
        except Exception as e:
            logger.exception(f"Failed to delete model, Reason: {e}")
            raise
