from dataclasses import replace

from distribution_inference.config import DatasetConfig, TrainConfig, AttackConfig


def get_dfs_for_victim_and_adv(base_data_config: DatasetConfig,
                               prop_value=None):
    """
        Starting from given base data configuration, make two copies.
        One with the split as 'adv', the other as 'victim'
    """
    base_data_config_ = base_data_config
    if prop_value is not None:
        # Replace value in data config
        base_data_config_ = replace(base_data_config)
        base_data_config_.value = prop_value

    config_adv = replace(base_data_config_)
    config_adv.split = "adv"
    config_victim = replace(base_data_config_)
    config_victim.split = "victim"
    return config_adv, config_victim


def get_train_config_for_adv(train_config: TrainConfig,
                             attack_config: AttackConfig):
    """
        Check if misc training config for adv is different.
        If yes, make one and return. Else use same as base config.
    """
    if attack_config.adv_diff_misc_config:
        train_config_adv = replace(train_config)
        train_config_adv.misc_config = attack_config.adv_misc_config
    else:
        train_config_adv = train_config
    return train_config_adv
