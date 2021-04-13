from sisense_sync.backup import Backup


def main():
    backup = Backup()
    backup.save_dashboards()
    backup.save_models()
    backup.commit()
