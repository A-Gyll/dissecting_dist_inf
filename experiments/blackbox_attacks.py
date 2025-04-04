"""
    Script for executing black-box inference attacks.
"""
from simple_parsing import ArgumentParser
from pathlib import Path
import os
from distribution_inference.datasets.utils import get_dataset_wrapper, get_dataset_information
from distribution_inference.attacks.blackbox.utils import get_attack, calculate_accuracies, get_vic_adv_preds_on_distr
from distribution_inference.attacks.blackbox.core import PredictionsOnDistributions
from distribution_inference.attacks.utils import get_dfs_for_victim_and_adv, get_train_config_for_adv
from distribution_inference.config import DatasetConfig, AttackConfig, BlackBoxAttackConfig, TrainConfig
from distribution_inference.utils import flash_utils
from distribution_inference.logging.core import AttackResult


if __name__ == "__main__":
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        "--en", help="experiment name",
        type=str, required=True)
    parser.add_argument(
        "--load_config", help="Specify config file",
        type=Path, required=True)
    parser.add_argument('--gpu',
                        default='0,1,2,3', help="device number")
    parser.add_argument(
        "--victim_path", help="path to victim'smodels directory",
        type=str, default=None)
    parser.add_argument(
        "--prop", help="Property for which to run the attack",
        type=str, default=None)
    args = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    attack_config: AttackConfig = AttackConfig.load(
        args.load_config, drop_extra_fields=False)

    # Use given prop (if given) or the one in the config
    if args.prop is not None:
        attack_config.train_config.data_config.prop = args.prop

    # Extract configuration information from config file
    bb_attack_config: BlackBoxAttackConfig = attack_config.black_box
    train_config: TrainConfig = attack_config.train_config
    data_config: DatasetConfig = train_config.data_config
    if train_config.misc_config is not None:
        # TODO: Figure out best place to have this logic in the module
        if train_config.misc_config.adv_config:
            # Scale epsilon by 255 if requested
            if train_config.misc_config.adv_config.scale_by_255:
                train_config.misc_config.adv_config.epsilon /= 255

    # Print out arguments
    flash_utils(attack_config)
    # Define logger
    logger = AttackResult(args.en, attack_config)

    # Get dataset wrapper
    ds_wrapper_class = get_dataset_wrapper(data_config.name)

    # Get dataset info object
    ds_info = get_dataset_information(data_config.name)()

    # Create new DS object for both and victim
    data_config_adv_1, data_config_vic_1 = get_dfs_for_victim_and_adv(
        data_config)
    
    # creates celeb dataset wrapper class
        # uses base class initiliazation to set self.ratio=data_config.value
        # ratio value = train config value specified in attack config
            # value is the same for both the vic and adv 1
    ds_vic_1 = ds_wrapper_class(
        data_config_vic_1,
        skip_data=True,
        label_noise=train_config.label_noise,
        epoch=attack_config.train_config.save_every_epoch)
    #HERE!
    ds_adv_1 = ds_wrapper_class(data_config_adv_1)
    train_adv_config = get_train_config_for_adv(train_config, attack_config)

    def single_evaluation(models_1_path=None, models_2_paths=None):
        """
        At this point we already have the ds configs for the victim and adv
        for the property ratio that we specify in the train_config portion of the
        attack config. This is the ratio the victim model was training on.

        This is also the value that we use for the adv_1 and which we expect to 
        produce predictions similar to the vic_1 model
        """

        # Load victim models for first value
        models_vic_1 = ds_vic_1.get_models(
            train_config,
            n_models=attack_config.num_victim_models,
            on_cpu=attack_config.on_cpu,
            shuffle=False,
            epochwise_version=attack_config.train_config.save_every_epoch,
            model_arch=attack_config.victim_model_arch,
            custom_models_path=models_1_path)
        if type(models_vic_1) == tuple:
                models_vic_1 = models_vic_1[0]

        # For each value (of property) asked to experiment with
        for prop_value in attack_config.values:
            """
            We are going to test the performance for every propery value
            that we specify having in the attack config. This means we need 
            adv models trained on each of these ratios.

            We get the adv and victim models for each of these ratios. 
            
            TODO: Why do we need to get the victim ratio for these a well? Where 
            and why do we use it? 
            """

            """
            Taking the same data configuration, but replacing the value with the prop
            value of interest and making adv/vic splits
            """
            data_config_adv_2, data_config_vic_2 = get_dfs_for_victim_and_adv(
                data_config, prop_value=prop_value)

            # Create new DS object for both and victim (for other ratio)
            """
            now have dataset configuration for both adv and victims
            """
            ds_vic_2 = ds_wrapper_class(
                data_config_vic_2, skip_data=True,
                label_noise=train_config.label_noise,
                epoch=attack_config.train_config.save_every_epoch)
            ds_adv_2 = ds_wrapper_class(data_config_adv_2)

            # Load victim models for other value
            """
            getting models for the ratio of interest for vic model
            passing in train_config, but not using that prop ratio
            """
            models_vic_2 = ds_vic_2.get_models(
                train_config, 
                n_models=attack_config.num_victim_models,
                on_cpu=attack_config.on_cpu,
                shuffle=False,
                epochwise_version=attack_config.train_config.save_every_epoch,
                model_arch=attack_config.victim_model_arch,
                custom_models_path=models_2_paths[i] if models_2_paths else None)
            if type(models_vic_2) == tuple:
                models_vic_2 = models_vic_2[0]
            for t in range(attack_config.tries):
                print("{}: trial {}".format(prop_value, t))
                """
                This should be the adv models with the vic model prop ratio
                """
                models_adv_1 = ds_adv_1.get_models(
                    train_adv_config,
                    n_models=bb_attack_config.num_adv_models,
                    on_cpu=attack_config.on_cpu,
                    model_arch=attack_config.adv_model_arch,
                    target_epoch = attack_config.adv_target_epoch)
                if type(models_adv_1) == tuple:
                    models_adv_1 = models_adv_1[0]
                models_adv_2 = ds_adv_2.get_models(
                    train_adv_config,
                    n_models=bb_attack_config.num_adv_models,
                    on_cpu=attack_config.on_cpu,
                    model_arch=attack_config.adv_model_arch,
                    target_epoch = attack_config.adv_target_epoch)
                if type(models_adv_2) == tuple:
                    models_adv_2 = models_adv_2[0]

                # Get victim and adv predictions on loaders for first ratio
                """
                property values for models
                    vic_1: value in data_config of attack_config
                    adv_1: value in data_config of attack_config
                    vic_2: cur property ratio from loop
                    adv_2: cur property ratio from loop
                """

                """
                adv preds uses the same loader 
                as victim in "get_vic_adv_preds_on_distr (attacks_blackbox_utils). This dataloader
                is used for every single set of models (vic1, adv1, vic2, adv2) unless otherwise
                specified. Ground truths are the same unless we shuffle data
                """
                # preds_adv_on_1: adv (trained on vic dist & diff dist)
                # preds_vic_on_1: vic (trained on vic dist & diff dist)
                # both prediciton are on victim dist
                preds_adv_on_1, preds_vic_on_1, ground_truth_1, not_using_logits = get_vic_adv_preds_on_distr(
                    models_vic=(models_vic_1, models_vic_2),
                    models_adv=(models_adv_1, models_adv_2),
                    ds_obj=ds_adv_1, # victim model distribution #HERE!
                    batch_size=bb_attack_config.batch_size,
                    epochwise_version=attack_config.train_config.save_every_epoch,
                    preload=bb_attack_config.preload,
                    multi_class=bb_attack_config.multi_class,
                    make_processed_version=attack_config.adv_processed_variant
                )
                # preds_adv_on_2: adv (trained on vic dist & diff dist)
                # preds_vic_on_2: vic (trained on vic dist & diff dist)
                # both prediciton are on diff dist from loop
                preds_adv_on_2, preds_vic_on_2, ground_truth_2, _ = get_vic_adv_preds_on_distr(
                    models_vic=(models_vic_1, models_vic_2),
                    models_adv=(models_adv_1, models_adv_2),
                    ds_obj=ds_adv_2, # diff loop dist
                    batch_size=bb_attack_config.batch_size,
                    epochwise_version=attack_config.train_config.save_every_epoch,
                    preload=bb_attack_config.preload,
                    multi_class=bb_attack_config.multi_class,
                    make_processed_version=attack_config.adv_processed_variant
                )

                """
                Each preds_<type>_on_<dist> contains 2 sets of predictions. 
                The first is the property 1 (original in training) and the second
                is property 2 (current loop property value)

                These 2 sets of prediction are each [#models, #predictions] shape
                """
                preds_adv = PredictionsOnDistributions(
                    preds_on_distr_1=preds_adv_on_1, # adv(org), adv(new prop) on adv(org)
                    preds_on_distr_2=preds_adv_on_2 # adv(org), adv(new prop) on adv(new prop)
                )
                preds_vic = PredictionsOnDistributions(
                    preds_on_distr_1=preds_vic_on_1, # vic(org), vic(new propr) on adv(org)
                    preds_on_distr_2=preds_vic_on_2 # vic(org), vic(new propr) on adv(new prop)
                )

                # TODO: Need a better (and more modular way) to handle
                # the redundant code above.

                # For each requested attack
                for attack_type in bb_attack_config.attack_type:
                    # Create attacker object
                    attacker_obj = get_attack(attack_type)(bb_attack_config)
                    # Launch attack
                    result = attacker_obj.attack(
                        preds_adv, preds_vic,
                        ground_truth=(ground_truth_1, ground_truth_2),
                        calc_acc=calculate_accuracies,
                        epochwise_version=attack_config.train_config.save_every_epoch,
                        not_using_logits=not_using_logits,
                        regression = bb_attack_config.regression
                    )


                    logger.add_results(attack_type, prop_value,
                                       result[0][0], result[1][0])
                    print(result[0][0])
                    # Save predictions, if requested
                    if bb_attack_config.save and attacker_obj.supports_saving_preds:
                        save_dic = attacker_obj.wrap_preds_to_save(result)

                    # Keep saving results (more I/O, minimal loss of information in crash)
                    logger.save()

    if args.victim_path:
        def joinpath(x, y): return os.path.join(
            args.victim_path, str(x), str(y))
        for i in range(1, 3+1):
            models_1_path = joinpath(data_config.value, i)
            model_2_paths = [joinpath(v, i) for v in attack_config.values]
            single_evaluation(models_1_path, model_2_paths)
    else:
        single_evaluation()