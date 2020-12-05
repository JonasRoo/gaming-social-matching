from typing import List, Optional
from lol.models import Version, Champion
from lol.riot_interface.client_secrets import X_RIOT_TOKEN
from riotwatcher import LolWatcher

_DEFAULT_REGION = "euw1"


def fetch_static_data(also_fetch_queues: Optional[bool] = False):
    watcher = LolWatcher(api_key=X_RIOT_TOKEN)
    version = fetch_and_save_version(watcher=watcher)
    fetch_and_write_champs(watcher=watcher, version=version)


def fetch_and_save_version(
    watcher: LolWatcher, for_region: Optional[str] = None
) -> Version:
    for_region = for_region or _DEFAULT_REGION
    versions_resp = watcher.data_dragon.versions_for_region(for_region)
    version = Version._from_api_dict(api_response=versions_resp)
    version.save()
    return version


def fetch_and_write_champs(watcher: LolWatcher, version: Version):
    api_response = watcher.data_dragon.champions(version=version.champion)
    for raw_champ_data in api_response["data"].values():
        champ_dict = Champion._from_single_champ_dict(raw_champ_data, mode="dict")
        # TODO(jonas): this is a little less ugly
        unique_checks = {"id": champ_dict["id"], "version": champ_dict["version"]}
        remaining_attrs = {
            k: v for k, v in champ_dict.items() if k not in unique_checks
        }
        champ, _ = Champion.objects.update_or_create(
            **unique_checks, defaults=remaining_attrs
        )
        champ.save(version=version)
