from tqdm import tqdm
import os
import data_utils
import model_utils
import utils
FILTER = 'two_attr'

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--ratio1', type=float, default=0.5,
                        help='ratio for female')
    parser.add_argument('--ratio2', type=float, default=0.5,
                        help='ratio for white')
    parser.add_argument('--num', type=int, default=1000,
                        help='how many classifiers to train?')
    parser.add_argument('--split', choices=["adv", "victim"],
                        help='which split of data to use')
    parser.add_argument('--verbose', action="store_true",
                        help='print out per-classifier stats?')
    parser.add_argument('--offset', type=int, default=0,
                        help='start counting from here when saving models')
    args = parser.parse_args()
    utils.flash_utils(args)

    # Census Income dataset
    ds = data_utils.CensusTwo()
    iterator = range(1, args.num + 1)
    if not args.verbose:
        iterator = tqdm(iterator)

    for i in iterator:
        if args.verbose:
            print("Training classifier %d" % i)

        # Sample to qualify ratio, ultimately coming from fixed split
        # Ensures non-overlapping data for target and adversary
        # All the while allowing variations in dataset locally
        (x_tr, y_tr), (x_te, y_te), cols = ds.get_data(args.split,args.ratio1,args.ratio2)

        clf = model_utils.get_model()
        clf.fit(x_tr, y_tr.ravel())
        train_acc = 100 * clf.score(x_tr, y_tr.ravel())
        test_acc = 100 * clf.score(x_te, y_te.ravel())
        if args.verbose:
            print("Classifier %d : Train acc %.2f , Test acc %.2f\n" %
                  (i, train_acc, test_acc))
        save_path = model_utils.get_models_path(FILTER,args.split,";".join(str(args.ratio1),str(args.ratio2)))
        if not os.path.isdir(save_path):
            os.makedirs(save_path)
        model_utils.save_model(clf, os.path.join(save_path,
            str(i + args.offset) + "_%.2f" % test_acc))
