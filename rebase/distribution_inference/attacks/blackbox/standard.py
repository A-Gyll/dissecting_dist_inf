import numpy as np
from typing import Tuple
from typing import List, Callable

from distribution_inference.attacks.blackbox.core import Attack, threshold_test_per_dist, PredictionsOnDistributions
from sklearn.metrics import r2_score, mean_squared_error


class LossAndThresholdAttack(Attack):
    def attack(self,
               preds_adv: PredictionsOnDistributions,
               preds_vic: PredictionsOnDistributions,
               ground_truth: Tuple[List, List] = None,
               calc_acc: Callable = None,
               epochwise_version: bool = False,
               not_using_logits: bool = False,
               regression: bool = False):
        
        """
            Perform Threshold-Test and Loss-Test attacks using
            given accuracies of models.
        """
        assert calc_acc is not None, "Must provide function to compute accuracy"
        assert ground_truth is not None, "Must provide ground truth to compute accuracy"
        assert not (
            self.config.multi2 and self.config.multi), "No implementation for both multi model"
        assert not (
            epochwise_version and self.config.multi2), "No implementation for both epochwise and multi model"
        
        if regression:
            def calc_regression_metric_mse(data, labels, multi_class=False):
                n_models = data.shape[1]
                mse_scores = np.zeros(n_models)
                for i in range(n_models):
                    y_pred = data[:, i]
                    mse_scores[i] = mean_squared_error(labels, y_pred)
                return mse_scores

            def calc_regression_metric_r2(data, labels, multi_class=False):
                print("using r2 metric")
                n_models = data.shape[1]
                r2_scores = np.zeros(n_models)
                # Compute r² for each model independently
                for i in range(n_models):
                    y_pred = data[:, i]
                    ss_res = np.sum((labels - y_pred) ** 2)
                    ss_tot = np.sum((labels - np.mean(labels)) ** 2)
                    # Avoid division by zero in case ss_tot is zero
                    r2_scores[i] = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
                return r2_scores

            # calc_acc = calc_regression_metric_r2
            print("using mse metric")
            calc_acc = calc_regression_metric_mse
        
        # Get accuracies on first data distribution using prediction from shadow/victim models
        adv_accs_1, victim_accs_1, acc_1 = threshold_test_per_dist(
            calc_acc,
            preds_adv.preds_on_distr_1,
            preds_vic.preds_on_distr_1,
            ground_truth[0],
            self.config,
            epochwise_version=epochwise_version)
        # Get accuracies on second data distribution
        adv_accs_2, victim_accs_2, acc_2 = threshold_test_per_dist(
            calc_acc,
            preds_adv.preds_on_distr_2,
            preds_vic.preds_on_distr_2,
            ground_truth[1],
            self.config,
            epochwise_version=epochwise_version)
        # adv_acc: how often the theshold rule correctly distinguishes between the 
        # adv two different prediction sets (assume victim can't really be better than this)

        # Get best adv accuracies for both distributions, across all ratios
        chosen_distribution = 0
        if np.max(adv_accs_1) > np.max(adv_accs_2):
            adv_accs_use, victim_accs_use = adv_accs_1, victim_accs_1
        else:
            adv_accs_use, victim_accs_use = adv_accs_2, victim_accs_2
            chosen_distribution = 1

        # Of the chosen distribution, pick the one with the best accuracy
        # out of all given ratios
        chosen_ratio_index = np.argmax(adv_accs_use)
        if epochwise_version:
            victim_acc_use = [x[chosen_ratio_index] for x in victim_accs_use]
        else:
            victim_acc_use = victim_accs_use[chosen_ratio_index]
        # victim_accuracy: how often the same adv theshold correctly distinguishes
        # between the victim's model predictions

        # Loss test
        if epochwise_version:
            basic = []
            for i in range(acc_1[0].shape[0]):
                basic.append(
                    self._loss_test(
                        (acc_1[0][i], acc_1[1][i]),
                        (acc_2[0][i], acc_2[1][i])
                    )
                )
            basic_chosen = [x[chosen_ratio_index] for x in basic]
        else:
            if self.config.multi2:
                basic = self._loss_multi(acc_1, acc_2)
            else:
                basic = self._loss_test(acc_1, acc_2)
            basic_chosen = basic[chosen_ratio_index]
        # basic_chosen: how effective the loss test can discriminate btw the two sets
        choice_information = (chosen_distribution, chosen_ratio_index)
        # returning [(threshold test results, loss test results), theshold accuracy on adversarial model (upper bound on vic acc), choice info]
        print([[(victim_acc_use, basic_chosen)], [adv_accs_use[chosen_ratio_index]], choice_information])
        return [[(victim_acc_use, basic_chosen)], [adv_accs_use[chosen_ratio_index]], choice_information]

    def _loss_test(self, acc_1, acc_2):
        basic = []
        # I think the config.ratios is the data split ratios
        for r in range(len(self.config.ratios)):
            preds_1 = (acc_1[0][r, :] > acc_2[0][r, :])
            preds_2 = (acc_1[1][r, :] <= acc_2[1][r, :])
            basic.append(100*(np.mean(preds_1) + np.mean(preds_2)) / 2)
        return basic

    def _loss_multi(self, acc_1, acc_2):
        basic = []
        l = acc_1[0].shape[1]
        for r in range(len(self.config.ratios)):
            preds_1 = []
            preds_2 = []
            for i in range(l):
                # Pick 'multi2' random samples
                sampling = np.random.permutation(l)[:self.config.multi2]
                # Equivalent to majority voting on each model's prediction
                preds_1.append(
                    np.mean(acc_1[0][r, sampling] > acc_2[0][r, sampling]) >= 0.5)
                preds_2.append(
                    np.mean(acc_1[1][r, sampling] <= acc_2[1][r, sampling]) >= 0.5)
            basic.append(100*(np.mean(preds_1) + np.mean(preds_2)) / 2)
        return basic
