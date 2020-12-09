from typing import List, Optional
import requests
from lol.models import Version, Champion, Queue
from lol.riot_interface.client_secrets import X_RIOT_TOKEN
from riotwatcher import LolWatcher

_DEFAULT_REGION = "euw1"
_QUEUES_JSON_URI = "http://static.developer.riotgames.com/docs/lol/queues.json"


def fetch_static_data(also_fetch_queues: Optional[bool] = False) -> None:
    """
    Fetches all static data from the DDragon API.
    Static data that's fetched:
        > Version: versions for every static data type (e.g. champion, items). Creates a new instance on every call.
        > Champions: All champs in league. Updates or creates.

    Args:
        also_fetch_queues (Optional[bool], optional): If True, also fetches queue_types. This is generally not necessary (outside of initial loads). Defaults to False.
    """
    watcher = LolWatcher(api_key=X_RIOT_TOKEN)
    version = fetch_and_save_version(watcher=watcher)
    fetch_and_write_champs(watcher=watcher, version=version)
    if also_fetch_queues:
        fetch_and_write_queue_types(watcher=watcher)


def fetch_and_save_version(
    watcher: LolWatcher, for_region: Optional[str] = None
) -> Version:
    """
    Fetches the newest game version(s) and saves a new instance to the DB.
    """
    # versions are region specific.
    # This should almost never be an issue, but regions can be on different patches.
    for_region = for_region or _DEFAULT_REGION
    versions_resp = watcher.data_dragon.versions_for_region(for_region)
    version = Version._from_api_dict(api_response=versions_resp)
    version.save()
    return version


def fetch_and_write_champs(watcher: LolWatcher, version: Version) -> None:
    """
    Fetches all current champs, and either updates existing ones or writes new instances.

    Args:
        watcher (LolWatcher): Current watcher to query DDragon with.
        version (Version): A valid version.
    """
    api_response = watcher.data_dragon.champions(version=version.champion)
    for raw_champ_data in api_response["data"].values():
        champ_dict = Champion._from_single_champ_dict(raw_champ_data, mode="dict")
        # TODO(jonas): this is a little less ugly
        unique_checks = {"id": champ_dict["id"]}
        remaining_attrs = {
            k: v for k, v in champ_dict.items() if k not in unique_checks
        }
        champ, _ = Champion.objects.update_or_create(
            **unique_checks, defaults=remaining_attrs
        )
        champ.save(version=version)


def fetch_and_write_queue_types(watcher: LolWatcher) -> None:
    """
    Fetches and saves to the database all queue types (e.g. SR RANKED SOLO/DUO).
    If fetching of data is successful, current queues are deleted.

    Args:
        watcher (LolWatcher): Current LolWatcher instance.
    """
    try:
        r = requests.get(url=_QUEUES_JSON_URI)
        r.raise_for_status()
        data = r.json()
        # since this won't be loaded often and it's a wholistic truth, we can safely whipe the table.
        Queue.objects.all().delete()
        for queue in data:
            # write them all to the database
            Queue._from_api_dict(queue).save()
    except requests.exceptions.RequestException as e:
        # extremely generic exception to avoid causing issues in application
        # if we somehow encountered an error, safely abort
        print(f"Error fetching queues: Error encountered:\n{e}")