import logging

from .archive import ArchiveManager
from .config import load_config
from .downloader import MetadataDownloader
from .git_ops import run_git_sync
from .notifier import send_notification
from .utils import get_dir_size_human


def run_job(config_path: str, dry_run: bool, verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    config = load_config(config_path)
    archive = ArchiveManager(config.archive_file)
    downloader = MetadataDownloader(config, archive)

    newly_downloaded = 0
    errors = []

    try:
        candidates = downloader.search_videos()
        for entry in candidates:
            try:
                if downloader.process_video(entry, dry_run=dry_run):
                    newly_downloaded += 1
            except Exception as e:
                errors.append(str(e))

        git_success, git_msg = (
            (True, "Skipped") if dry_run else run_git_sync(config, newly_downloaded)
        )

        status = "success"
        if errors or not git_success:
            status = "partial" if newly_downloaded > 0 else "failure"

        # Final Summary
        total_size = get_dir_size_human(config.data_dir)
        summary = (
            f"Job: {config.get('job_name')}\n"
            f"Query: {config.get('search', 'query')}\n"
            f"New Files: {newly_downloaded}\n"
            f"Git Status: {git_msg}\n"
            f"Data Size: {total_size}\n"
            f"Status: {status.upper()}"
        )

        if errors:
            summary += f"\nErrors: {len(errors)} occurred."

        if not dry_run:
            notify_level = config.get("telegram", f"level_on_{status}", default="info")
            send_notification(config, notify_level, summary)

        print(summary)
        return 0 if status == "success" else (2 if status == "partial" else 1)

    except Exception as e:
        logging.error(f"Fatal job failure: {e}")
        if not dry_run:
            send_notification(config, "error", f"Job Failed: {e}")
        return 1
