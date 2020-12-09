from typing import Dict, Union
from datetime import datetime, timedelta
from numbers import Number
import warnings
from django.db import models
from common_utils import json_utils, time_utils


class Game(models.Model):
    platform = models.CharField(max_length=16)
    game = models.BigIntegerField()
    champion = models.IntegerField()
    queue = models.IntegerField()
    season = models.IntegerField()
    timestamp = models.DateTimeField()
    role = models.CharField(max_length=32, blank=True, null=True)
    lane = models.CharField(max_length=32, blank=True, null=True)

    def pre_save(self, *args, **kwargs):
        if isinstance(self.timestamp, Number):
            self.timestamp = time_utils.get_tz_aware_dt_from_timestamp(self.timestamp)

    @classmethod
    def api_model_map(cls) -> Dict[str, str]:
        return {
            "platformId": "platform",
            "gameId": "game",
        }

    @classmethod
    def _from_api_dict(cls, api_response: Dict[str, Union[str, int]]) -> "Game":
        mapper = cls.api_model_map()
        for k, v in mapper.items():
            api_response[v] = api_response.pop(k)
        return cls(**api_response)


# V -------------- ddragon -------------- V
class Version(models.Model):
    """
    Represents a response of the version API.
    A 'version' string is necessary to query the DDragon endpoints.
    Example: `10.24.1`.
    WARNING: versions are region specific!
    Polled from the Riot API:
        -> list of all versions (DESC): https://ddragon.leagueoflegends.com/api/versions.json
        -> versions per realm: https://ddragon.leagueoflegends.com/realms/na.json
    """

    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    # TODO(jonas): add region field as enum
    item = models.CharField(max_length=64)
    rune = models.CharField(max_length=64)
    mastery = models.CharField(max_length=64)
    summoner = models.CharField(max_length=64)
    champion = models.CharField(max_length=64)
    profile_icon = models.CharField(max_length=64)
    map = models.CharField(max_length=64)
    language = models.CharField(max_length=64)
    sticker = models.CharField(max_length=64)
    cdn = models.URLField()

    class Meta:
        ordering = ["-date_added"]

    @classmethod
    def _get_api_model_map(cls) -> Dict[str, str]:
        d = {}
        for field in cls._meta.get_fields():
            if field.name not in ["id", "pk", "date_added", "cdn"]:
                d[f"n-{field.name.replace('_', '')}"] = field.name
        d["cdn"] = "cdn"
        return d

    @classmethod
    def _from_api_dict(cls, api_response: Dict[str, str]) -> "Version":
        api_response = json_utils.flatten_dict_by_joining(api_response)
        formatted_response = {}
        mapper = cls._get_api_model_map()
        for k, v in mapper.items():
            formatted_response[v] = api_response.pop(k)
        return cls(**formatted_response)

    @property
    def last_version(self):
        version = self.objects.latest(field_name="date_added")
        if datetime.utcnow() - version.date_added > timedelta(days=1):
            warnings.warn(
                f"Latest version update is more than 1 day old. (Last pulled: {version.date_added})"
            )
        return version


class Champion(models.Model):
    """
    Represents a champion within League of Legends.
    Polled from the Riot API:
        -> http://ddragon.leagueoflegends.com/cdn/{{version}}/data/en_US/champion.json
    """

    id = models.IntegerField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.CharField(max_length=64)
    internal_name = models.CharField(max_length=64, blank=False, null=False)
    name = models.CharField(max_length=64, blank=False, null=False)
    title = models.CharField(max_length=128, blank=True, null=True)
    splash = models.URLField(blank=True, null=True)
    loading = models.URLField(blank=True, null=True)
    square = models.URLField(blank=True, null=True)
    tags = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        unique_together = ("id", "version")

    # The "0" suffix corresponds to the base skin (higher number for skins...)
    def _construct_full_splash_url(self, version: Version) -> str:
        return f"{version.cdn}/img/champion/splash/{self.internal_name}_0.jpg"

    def _construct_full_loading_url(self, version: Version) -> str:
        return f"{version.cdn}/img/champion/loading/{self.internal_name}_0.jpg"

    # Champion squares are NOT skin dependent
    def _construct_full_square_url(self, version: Version) -> str:
        return f"{version.cdn}/{version.champion}/img/champion/{self.internal_name}.png"

    @classmethod
    def _get_api_model_map(cls) -> Dict[str, str]:
        return {
            "key": "id",
            "version": "version",
            "id": "internal_name",
            "name": "name",
            "title": "title",
            "tags": "tags",
        }

    @classmethod
    def _from_single_champ_dict(
        cls,
        single_champ_dict: Dict[str, str],
        mode: str = "instance",
    ) -> "Champion":
        formatted_response = {}
        mapper = cls._get_api_model_map()
        for k, v in mapper.items():
            formatted_response[v] = single_champ_dict.pop(
                " ".join(k) if isinstance(k, (list, tuple)) else k
            )

        if mode == "instance":
            return cls(**formatted_response)
        elif mode == "dict":
            return formatted_response
        else:
            raise AttributeError(f"invalid mode!")

    def save(self, version: Version = None, *args, **kwargs):
        if version:
            self.splash = self._construct_full_splash_url(version)
            self.loading = self._construct_full_loading_url(version)
            self.sprite = self._construct_full_square_url(version)
        super().save(*args, **kwargs)


class Queue(models.Model):
    """
    Represents a queue type within League of Legends.
    Examples:
        > 5x5 RANKED_SOLO_DUO_SR
        > 5x5 ARAM
    Polled from the Riot API:
        -> http://static.developer.riotgames.com/docs/lol/queues.json
    """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    notes = models.CharField(max_length=128, blank=True, null=True)

    @classmethod
    def _get_api_model_map(cls) -> Dict[str, str]:
        return {
            "queueId": "id",
            "map": "name",
        }

    @classmethod
    def _from_api_dict(cls, single_queue_map: Dict[str, str]) -> "Queue":
        mapper = cls._get_api_model_map()
        for k, v in mapper.items():
            single_queue_map[v] = single_queue_map.pop(k)
        return cls(**single_queue_map)


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.CharField(max_length=64)
    name = models.CharField(max_length=128, blank=False, null=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    icon = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ("id", "version")
