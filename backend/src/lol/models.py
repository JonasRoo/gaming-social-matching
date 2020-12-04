from typing import Dict, Union
from django.db import models


class Game(models.Model):
    platform = models.CharField(max_length=16)
    game = models.BigIntegerField()
    champion = models.IntegerField()
    queue = models.IntegerField()
    season = models.IntegerField()
    timestamp = models.BigIntegerField()
    role = models.CharField(max_length=32, blank=True, null=True)
    lane = models.CharField(max_length=32, blank=True, null=True)

    @property
    def api_model_map() -> Dict[str, str]:
        return {
            "platformId": "platform",
            "gameId": "game",
        }

    @classmethod
    def _from_api_dict(cls, api_response: Dict[str, Union[str, int]]) -> "Game":
        mapper = cls.api_model_map
        for k, v in mapper.items():
            api_response[v] = api_response.pop(k)
        return cls(**api_response)


# V -------------- ddragon -------------- V
class Version(models.Model):
    date_added = models.DateTimeField(auto_now_add=True, db_index=True)
    item = models.CharField(max_length=64)
    rune = models.CharField(max_length=64)
    mastery = models.CharField(max_length=64)
    summoner = models.CharField(max_length=64)
    champion = models.CharField(max_length=64)
    profile_icon = models.CharField(max_length=64)
    map = models.CharField(max_length=64)
    language = models.CharField(max_length=64)
    sticker = models.CharField(max_length=64)

    class Meta:
        ordering = ["-date_added"]

    @property
    def api_model_map() -> Dict[str, str]:
        return {
            "profileicon": "profile_icon",
        }

    @classmethod
    def _from_api_dict(cls, api_response: Dict[str, str]) -> "Version":
        mapper = cls.api_model_map
        for k, v in mapper.items():
            api_response[v] = api_response.pop(k)
        return cls(**api_response)


# TODO(jonas): how do I dynamically "generate" the splash / sprite URL prefixes
class Champion(models.Model):
    """
    Represents a champion within League of Legends.
    Polled from the Riot API:
        ->
    """

    id = models.IntegerField(primary_key=True)
    version = models.ForeignKey(to=Version, to_field="champion", db_column="version")
    name = models.CharField(max_length=64, blank=False, null=False)
    title = models.CharField(max_length=128, blank=True, null=True)
    splash = models.URLField(blank=True, null=True)
    sprite = models.URLField(blank=True, null=True)
    tags = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        unique_together = ("id", "version")


class Queue(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64, blank=False, null=False)


class Item(models.Model):
    id = models.IntegerField(primary_key=True)
    version = models.ForeignKey(to=Version, to_field="item", db_column="version")
    name = models.CharField(max_length=128, blank=False, null=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    icon = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ("id", "version")
