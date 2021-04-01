from sisense_sync.client import client
from loguru import logger

import os
import git
import shutil


class Backup():

    def __init__(self):
        self.client = client
        self.storage = os.path.join(os.getcwd(), 'work')
        self.remote = client.param_dict['repo']
        self.env = client.param_dict['env']
        self._clean_checkout()

    def _clean_checkout(self):
        if os.path.isdir(self.storage):
            try:
                logger.warning(f"Cleaning {self.storage}")
                shutil.rmtree(self.storage)
            except Exception as e:
                logger.exception(f"Failed to delete {self.storage}, Reason: {e}")
                raise

        self.repo = git.Repo.clone_from(self.remote, self.storage, multi_options=['--depth 1'], branch="main")

    def _get_dashboards(self):
        self.dashboards = self.client.get_dashboards()
        return self.dashboards

    def _get_models(self):
        self.models = self.client.get_data_models()
        return self.models

    def save_models(self):
        os.makedirs(os.path.join(self.storage, f"models/{self.env}"), exist_ok=True)

        for model in self._get_models():
            oid = model.get_oid()
            model.export_to_smodel(f"work/models/{self.env}/{oid}.smodel")
            logger.opt(colors=True).success(f"Downloaded model: <white>{oid}</white>")

    def save_dashboards(self):
        os.makedirs(os.path.join(self.storage, f"dashboards/{self.env}"), exist_ok=True)

        for dashboard in self._get_dashboards():
            oid = dashboard.get_oid()
            dashboard.export_to_dash(f"work/dashboards/{self.env}/{oid}.dash")
            logger.opt(colors=True).success(f"Downloaded dashboard: <white>{oid}</white>")

    def commit(self):
        self.repo.index.add([f"dashboards/{self.env}"])
        self.repo.index.add([f"models/{self.env}"])
        if self.repo.index.diff('HEAD'):
            logger.info(f"Commiting {self.storage}")
            self.repo.index.commit(f"Updating resources for {self.env}")
            self.repo.remotes.origin.push()
        else:
            logger.info(f"No changes detected")




def main():

    backup = Backup()
    backup.save_dashboards()
    backup.save_models()
    backup.commit()
