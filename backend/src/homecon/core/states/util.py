from typing import Union, Optional

from homecon.core.states.state import IStateManager


def config_state_paths_to_keys(config: Union[dict, list, str], state_manager: IStateManager):

    def try_get_state_key(path: str) -> Optional[int]:
        try:
            state = state_manager.get(path=path)
        except:
            pass
        else:
            if state is not None:
                return state.key

    def cond(v) -> bool:
        return isinstance(v, str) and v.startswith('/')

    if isinstance(config, dict):
        for key, val in config.items():
            if 'state' in key:
                if cond(val):
                    config[key] = try_get_state_key(val)
                elif isinstance(val, list):
                    config[key] = [try_get_state_key(v) if cond(v) else v for v in val]
                elif isinstance(val, dict):
                    config[key] = {k: try_get_state_key(v) if cond(v) else v for k, v in val.items()}
            elif isinstance(val, dict):
                config_state_paths_to_keys(val, state_manager)

    return config


def config_state_keys_to_paths(config: dict, state_manager: IStateManager):
    """
    Checks for state keys in a dict and converts them to the correct state path.
    """

    def try_get_state_path(state_key: str) -> Optional[str]:
        try:
            state = state_manager.get(key=state_key)
        except:
            pass
        else:
            if state is not None:
                return state.path

    def cond(v) -> bool:
        return isinstance(v, str)

    if config is not None:
        for key, val in config.items():
            if 'state' in key:
                if isinstance(val, str):
                    config[key] = try_get_state_path(val)
                elif isinstance(val, list):
                    config[key] = [try_get_state_path(v) if cond(v) else v for v in val]
                elif isinstance(val, dict):
                    config[key] = {k: try_get_state_path(v) if cond(v) else v for k, v in val.items()}
            elif isinstance(val, dict):
                config[key] = config_state_keys_to_paths(val, state_manager)

    return config
