"""Stub OmegaConf module for optional dependency gating."""

class DictConfig(dict):
    pass


class OmegaConf:
    @staticmethod
    def to_container(cfg, resolve=False):
        return {}

    @staticmethod
    def to_yaml(cfg):
        return ""

    @staticmethod
    def select(cfg, key):
        return None
