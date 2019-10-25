# Imports
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision import models
from torch.autograd import Variable
# FP 16 Nvidia APEX lib
from apex.fp16_utils import FP16_Optimizer

import numpy as np
import datajoint as dj
import time
import platform
import multiprocessing

kubernetes_tutorial = dj.create_virtual_module('kubernetes_tutorial', 'kubernetes_tutorial')

# Training Parameters
num_of_epochs = 10
batch_size = 256
shuffle = True

# Tracking loss and history
previous_loss = 0.0
epoch_score_history = []

# Normlized Dataset
transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

# Training set
trainset = torchvision.datasets.CIFAR100(root='./data', train=True, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=2)

# Test set
testset = torchvision.datasets.CIFAR100(root='./data', train=False, download=True, transform=transform)
test_loader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)

# Use GPU if avaliable
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('GPU_Model: ' + torch.cuda.get_device_name(device.index))

# Model_32_bit
model = models.resnet50().half().to(device)
print(model)

optimizer = optim.Adam(model.parameters())
# Pass in the 32 optimizer into this wrapper. For details on "128" please refer to gradient underflow section (NEW CHANGE)
optimizer = FP16_Optimizer(optimizer, static_loss_scale=128) 
criterion = nn.CrossEntropyLoss()

# Training Model
start_time = time.time()
for epoch in range(num_of_epochs):
    # Clear epoc history
    epoch_loss_history = []
    
    for data in train_loader:
        inputs, targets = data
        
        # Send to device
        inputs = inputs.half().to(device) # Call .half() (NEW CHANGE)
        targets = targets.to(device)
        
        # Zero out grads
        optimizer.zero_grad()
        
        outputs = model(inputs)
        loss = criterion(outputs.float(), targets)
        
        # Instead of calling loss.backward() call optimizer.backward(loss) instead (NEW CHANGE)
        optimizer.backward(loss)
        optimizer.step()
        
        # Keep track of loss at each batch
        epoch_loss_history.append(loss.item())
        
    current_epoc_loss = np.array(epoch_loss_history).mean()
    print("Epoch ", epoch + 1, " loss: ", current_epoc_loss)
    epoch_score_history.append(current_epoc_loss)

elapse_time = time.time() - start_time
print('Training Time = ' + str(elapse_time))
kubernetes_tutorial.GPUTrainingPerformance().insert1(dict(computer_name=platform.node(), cpu_core_count=multiprocessing.cpu_count(), gpu_model=torch.cuda.get_device_name(device.index), training_time=elapse_time))