import numpy as np
import torch
from cv2 import imread, resize
import scipy.io as sio
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision import transforms
from sys import platform
import pickle
import os
from PIL import Image


im_trans = transforms.Compose([
    Image.fromarray,
    transforms.ToTensor(),
    transforms.Normalize([.5, .5, .5], [.5, .5, .5]),
])


class BodyMapDataset(Dataset):
    def __init__(self, data_root, dataset, dim=512, max_size=-1, device=None, transform=im_trans):
        
        super(BodyMapDataset, self).__init__()
        # Set image transforms and device
        self.device = torch.device('cuda') if device is None else device
        self.transform = transform
        self.pix_dim = (dim, dim, 3)
        self.im_root = data_root
        
        # Prepare train/test split
        self.names = np.loadtxt(os.path.join(self.im_root, 'input_%s.txt'%(dataset)), dtype=str)[:max_size]
        self.len =  len(self.names)
        self.im_names = [os.path.join(self.im_root, 'GT_output', im_name) for im_name in self.names]
    
    def __getitem__(self, id):

        img = self.transform(resize(imread(self.im_names[id]), self.pix_dim[:-1]))

        return img
        
    def __len__(self):
        return len(self.names)


if __name__ == '__main__':

    train_dataset = BodyMapDataset(data_root="./data", dataset="PoseRandom-stretch", cls_num=51, dim=256)
    trainset_loader = DataLoader(
        dataset=train_dataset,
        batch_size=1,
        drop_last=True,
        shuffle=True,
        num_workers=10
    )
    from tqdm import tqdm
    mat = torch.zeros(4150, 51)
    for idx, (img, label) in enumerate(tqdm(trainset_loader)):
        mat[idx] = label.flatten()
    np.save("mean-var.npy", {'mean':torch.mean(mat,dim=0).numpy(), 'std':torch.std(mat, dim=0).numpy()})

    print(torch.mean(mat, dim=0), torch.std(mat, dim=0))
    
    
    
