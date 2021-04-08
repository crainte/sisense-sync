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
            # By default shallow only pulls the tip of a single branch, we require
            # all defined remote branches so we need the --no-single-branch flag
            self.repo = git.Repo.clone_from(self.remote, self.storage, multi_options=['--depth 1','--no-single-branch'])
        except Exception as e:
            logger.exception(f"Failed to clone repo {self.remote}, Reason: {e}")
            raise

        try:
            # We need to figure out if this is a new branch, or we're working with
            # a pre-existing one
            self.repo.git.checkout(self.env)
        except Exception as e:
            logger.warning(f"Failed to checkout branch {self.env}")
            try:
                # No remote, checkout orphan
                self.repo.git.checkout(["--orphan", self.env])
                # Clean staging area
                self.repo.git.rm(".", ["-rf"])
                # Create initial empty commit to avoid reference issues
                self.repo.git.commit(["--allow-empty","-m","[bot] Initial Commit"])
                logger.success(f"Created clean orphan branch {self.env}")
            except Exception as e:
                logger.exception(f"Failed to create new branch {self.env}, Reason: {e}")
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
        ref = git.RemoteReference(self.repo, f"refs/remotes/origin/{self.env}")
        self.repo.head.reference.set_tracking_branch(ref)
        # Add directories
        self.repo.index.add([f"{self.storage}/dashboards/"])
        self.repo.index.add([f"{self.storage}/models/"])
        if self.repo.index.diff('HEAD'):
            try:
                self.repo.index.commit(f"[bot] Updating resources")
                origin = self.repo.remote()
                info = origin.push(self.env)[0]
                if "rejected" in info.summary:
                    logger.error(f"Failed: {info.summary}")
                else:
                    logger.success(info.summary)
            except Exception as e:
                logger.exception(f"Failed to commit changes, Reason: {e}")
                raise
        else:
            logger.info(f"No changes detected")


backup = Backup()
