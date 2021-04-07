from sisense_sync.client import client
from loguru import logger

import os
import git
import json
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

        try:
            self.repo = git.Repo.clone_from(self.remote, self.storage, multi_options=['--depth 1'])
            self.repo.git.checkout('HEAD', b=self.env)
        except Exception as e:
            logger.exception(f"Failed to clone repo {self.remote}, Reason: {e}")
            raise

    def _get_dashboards(self):
        self.dashboards = self.client.get_dashboards()
        return self.dashboards

    def _get_models(self):
        self.models = self.client.get_data_models()
        return self.models

    def _pretty(self, file):
        try:
            with open(file, "r+") as f:
                data = json.load(f)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
                f.close()
        except Exception as e:
            logger.exception(f"Failed to format file {file}, Reason: {e}")

    def save_models(self):
        os.makedirs(os.path.join(self.storage, f"models"), exist_ok=True)

        for model in self._get_models():
            oid = model.get_oid()
            try:
                model.export_to_smodel(f"{self.storage}/models/{oid}.smodel")
            except Exception as e:
                logger.exception(f"Failed to export {oid}.smodel, Reason: {e}")
                raise
            logger.opt(colors=True).success(f"Downloaded model: <white>{oid}</white>")
            self._pretty(f"{self.storage}/models/{oid}.smodel")

    def save_dashboards(self):
        os.makedirs(os.path.join(self.storage, f"dashboards"), exist_ok=True)

        for dashboard in self._get_dashboards():
            oid = dashboard.get_oid()
            try:
                dashboard.export_to_dash(f"{self.storage}/dashboards/{oid}.dash")
            except Exception as e:
                logger.exception(f"Failed to export {oid}.dash, Reason: {e}")
                raise
            logger.opt(colors=True).success(f"Downloaded dashboard: <white>{oid}</white>")
            self._pretty(f"{self.storage}/dashboards/{oid}.dash")

    def commit(self):
        self.repo.index.add([f"dashboards/"])
        self.repo.index.add([f"models/"])
        if self.repo.index.diff('HEAD'):
            try:
                self.repo.index.commit(f"Updating resources for {self.env}")
                # Set this branch to track remote
                ref = git.RemoteReference(self.repo, f"refs/remotes/origin/{self.env}")
                self.repo.head.reference.set_tracking_branch(ref)
                origin = self.repo.remote()
                origin.push()
                logger.success("Changes commited")
            except Exception as e:
                logger.exception(f"Failed to commit changes, Reason: {e}")
                raise
        else:
            logger.info(f"No changes detected")


backup = Backup()
