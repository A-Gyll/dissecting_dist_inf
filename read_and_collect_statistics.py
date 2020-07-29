import numpy as np
import torch as ch
from tqdm import tqdm
import utils


if __name__ == "__main__":
	
	# Get training-set images and model
	constants = utils.BinaryCIFAR("/p/adversarialml/as9rw/generated_images_binary_nodog/")
	cifar_constant = utils.CIFAR10()
	# model = cifar_constant.get_model("linf" , "vgg19")
	model = cifar_constant.get_model("nat" , "vgg19")
	
	# Get dataset
	ds = constants.get_dataset()
	_, data_loader = ds.make_loaders(batch_size=500, workers=8, shuffle_train=False, shuffle_val=False, data_aug=False, only_val=True)
	classwise_distr = np.zeros((10, 2))
	for (im, label) in tqdm(data_loader):
		logits, _ = model(im.cuda())
		preds = ch.argmax(logits, 1)
		for i, p in enumerate(preds):
			classwise_distr[p][label[i]] += 1

	mappinf = ["plane", "car", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]
	# Normalize
	classwise_distr[:, 0] /= classwise_distr[:, 0].sum()
	classwise_distr[:, 1] /= classwise_distr[:, 1].sum()
	for i, x in enumerate(mappinf):
		print("%s : %.2f & %.2f" % (x, classwise_distr[i][0] * 100, classwise_distr[i][1] * 100))
