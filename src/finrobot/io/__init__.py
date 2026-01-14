"""Backward compatibility - use finrobot.infrastructure.io instead."""

from finrobot.infrastructure.io.files import save_output, register_keys_from_json, SavePathType

__all__ = ["save_output", "register_keys_from_json", "SavePathType"]
