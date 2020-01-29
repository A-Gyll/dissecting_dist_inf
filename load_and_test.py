import torch as ch
from robustness.datasets import GenericBinary, CIFAR
from robustness.model_utils import make_and_restore_model
import numpy as np
from tqdm import tqdm

ds_path    = "/p/adversarialml/as9rw/datasets/cifar_binary/animal_vehicle_correct"
# model_path = "/p/adversarialml/as9rw/models_correct/edit_this.pt"
model_path   = "/p/adversarialml/as9rw/models_cifar10/delta_model.pt"
# model_path   = "/p/adversarialml/as9rw/models_cifar10/cifar_nat.pt"

# ds = GenericBinary(ds_path)
ds = CIFAR()

# Load model to attack
model_kwargs = {
	'arch': 'resnet50',
	'dataset': ds,
	'resume_path': model_path
}
model, _ = make_and_restore_model(**model_kwargs)
model.eval()

batch_size = 64

attack_x = np.load("attack_images.npy")
attack_y = np.load("attack_labels.npy")

accuracies = 0

for i in range(0, attack_y.shape[0], batch_size):
	im = attack_x[i:i + batch_size]
	im = ch.from_numpy(im).cuda()
	logits, _ = model(im)
	preds = ch.argmax(logits, 1).cpu().numpy()
	accuracies += np.sum(attack_y[i:i + batch_size] == preds)

print("Attack success rate : %f" % (1 - accuracies / attack_y.shape[0]))
