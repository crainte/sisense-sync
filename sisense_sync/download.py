from sisense_sync.backup import backup


def main():
    backup.save_dashboards()
    backup.save_models()
    backup.commit()
