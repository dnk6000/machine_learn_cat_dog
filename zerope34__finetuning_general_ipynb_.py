# -*- coding: utf-8 -*-
"""ZeroPE34 "FineTuning-general.ipynb"

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1F3STS3DyJG4TVvzg4l1Rz3HWyRuqQu4g

# Скачиваем датасет с Kaggle, распаковываем архив
"""

# Install Kaggle package
!pip install kaggle >> None

# Upload Kaggle API token (you need to have a kaggle.json file with your Kaggle API credentials)
from google.colab import files
# files.upload()

# Create a Kaggle folder and move the kaggle.json file there
!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/

# Change the permissions of the file
!chmod 600 ~/.kaggle/kaggle.json

# Download the Rock Paper Scissors dataset from Kaggle
# !kaggle datasets download -d sanikamal/rock-paper-scissors-dataset
!kaggle datasets download -d shaunthesheep/microsoft-catsvsdogs-dataset

# Unzip the dataset
# !unzip rock-paper-scissors-dataset.zip
!unzip microsoft-catsvsdogs-dataset.zip

import os
import matplotlib.pyplot as plt
from PIL import Image

# List files in the dataset folder
dataset_folder = "PetImages"  # This is the folder extracted from the downloaded zip
categories = os.listdir(dataset_folder)
print("Categories:", categories)

# List some images from one category
cat_folder = os.path.join(dataset_folder, "Dog")
cat_images = os.listdir(cat_folder)

# Display a few images
num_images = 5
fig, axes = plt.subplots(1, num_images, figsize=(20, 10))

for i in range(num_images):
    img_path = os.path.join(cat_folder, cat_images[i])
    img = Image.open(img_path)
    axes[i].imshow(img)
    axes[i].axis('off')

plt.show()

# delete corrupted images
from PIL import Image
import os

dest_dirs = ['PetImages/cat',
             'PetImages/dog'
             ]

for dataset_dir in dest_dirs:
  for filename in os.listdir(dataset_dir):
      file_path = os.path.join(dataset_dir, filename)
      try:
          img = Image.open(file_path)
          img.verify()  # Verify that it is an image
      except (IOError, SyntaxError) as e:
          print(f'Corrupted file found and removed: {file_path}')
          os.remove(file_path)

# Now, let's prepare the dataset for training and validation
import os
import shutil
from sklearn.model_selection import train_test_split

# Define paths
# data_dir = 'Rock-Paper-Scissors'
data_dir = 'PetImages'
work_dirs = ['train', 'val', 'test']

# Create train and val directories
for work_dir in work_dirs:
  if not os.path.exists(work_dir):
      new_dir = os.path.join(data_dir, work_dir)
      if not os.path.exists(new_dir):
        os.makedirs(new_dir)
      for class_name in ['cat', 'dog']:
        new_dir = os.path.join(data_dir, work_dir, class_name)
        print(new_dir)
        if not os.path.exists(new_dir):
          os.makedirs(new_dir)
        else:
          for filename in os.listdir(new_dir):
            file_path = os.path.join(new_dir, filename)
            os.remove(file_path)

# for work_dir in work_dirs:
#   for class_name in ['cat', 'dog']:
#       src_class_dir = os.path.join(data_dir, work_dir, class_name)
#       dst_class_dir_ = os.path.join(data_dir, work_dir)
#       dst_class_dir = os.path.join(work_dir, class_name)
#       if os.path.exists(src_class_dir):
#           # print('here 1')
#           for img in os.listdir(src_class_dir):
#               # print(f'here 2 {img}')
#               shutil.move(os.path.join(src_class_dir, img), os.path.join(dst_class_dir, img))

# print("Dataset preparation complete.")

import os
import shutil
import random

# Set the seed for reproducibility
random.seed(42)

# Directories
source_dirs = {'cat': 'PetImages/cat', 'dog': 'PetImages/dog'}
dest_dirs = {
    'train': {'cat': 'PetImages/train/cat', 'dog': 'PetImages/train/dog'},
    'val': {'cat': 'PetImages/val/cat', 'dog': 'PetImages/val/dog'},
    'test': {'cat': 'PetImages/test/cat', 'dog': 'PetImages/test/dog'}
}

# Create destination directories if they don't exist
for split in dest_dirs.values():
    for dir_path in split.values():
        os.makedirs(dir_path, exist_ok=True)

# Split ratios
train_ratio = 0.8
val_ratio = 0.1
test_ratio = 0.1

# Copy files
for label, source_dir in source_dirs.items():
    # List all files in the source directory
    all_files = os.listdir(source_dir)
    all_files = [f for f in all_files if os.path.isfile(os.path.join(source_dir, f))]

    # Shuffle files
    random.shuffle(all_files)

    # Calculate split sizes
    total_files = len(all_files)
    train_size = int(total_files * train_ratio)
    val_size = int(total_files * val_ratio)

    # Split the files
    train_files = all_files[:train_size]
    val_files = all_files[train_size:train_size + val_size]
    test_files = all_files[train_size + val_size:]

    # Copy files to train, val, and test directories
    for split, files in zip(['train', 'val', 'test'], [train_files, val_files, test_files]):
        for file_name in files:
            src_path = os.path.join(source_dir, file_name)
            dst_path = os.path.join(dest_dirs[split][label], file_name)
            shutil.copy2(src_path, dst_path)

print("Files have been successfully split into train, val, and test directories.")

# Count files in train, val, and test directories
dest_dirs = {
    'train': {'cat': 'PetImages/train/cat', 'dog': 'PetImages/train/dog'},
    'val': {'cat': 'PetImages/val/cat', 'dog': 'PetImages/val/dog'},
    'test': {'cat': 'PetImages/test/cat', 'dog': 'PetImages/test/dog'}
}
for split, dirs in dest_dirs.items():
    for label, dir_path in dirs.items():
        num_files = len(os.listdir(dir_path))
        print(f"Number of files in {split}/{label}: {num_files}")

import os

cat_directory = 'PetImages/Cat'  # Update the path as needed
files = os.listdir(cat_directory)

for file in files:
    print(file)

"""# Приводим данные к нужному формату, добавляем аугментации"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
import time
import os
import copy

from tqdm import tqdm

from torch.optim import lr_scheduler

# Define transformations
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224), # приведение к одному размеру
        transforms.RandomHorizontalFlip(), # аугментация - отзеркаливание
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # нормализация по каналам
    ]),
    'test': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# data_dir = 'Rock-Paper-Scissors'
data_dir = 'PetImages'
image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x]) for x in ['train', 'test']}
dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=32, shuffle=True, num_workers=4) for x in ['train', 'test']}
dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'test']}
class_names = image_datasets['train'].classes

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print('Running model on ', device)

"""# Визуализируем датасет"""

import matplotlib.pyplot as plt
import numpy as np
import torchvision

# Function to show images
def imshow(inp, title=None):
    """Imshow for Tensor."""
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    plt.xticks([])  # Remove x-ticks
    plt.yticks([])  # Remove y-ticks
    plt.pause(0.001)  # pause a bit so that plots are updated

# Get a batch of training data
inputs, classes = next(iter(dataloaders['train']))

# Make a grid from batch
out = torchvision.utils.make_grid(inputs)

# Plot the images
imshow(out, title=[class_names[x] for x in classes])

"""# Прописываем общую функцию для обучения"""

# Function to train the model
def train_model(model, criterion, optimizer, scheduler, num_epochs=5):
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print(f'Epoch {epoch}/{num_epochs - 1}')
        print('-' * 10)

        for phase in ['train', 'test']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in tqdm(dataloaders[phase]):
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            if phase == 'test' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best val Acc: {best_acc:.4f}')

    model.load_state_dict(best_model_wts)
    return model

"""# Задаем две модели - с нуля и предобученную. У предобученной замораживаем веса, запускаем их обучение"""

# Load ResNet-18 model trained from scratch
model_ft_scratch = models.resnet18(pretrained=False) # НЕ предобученная модель (pretrained=False)
num_ftrs = model_ft_scratch.fc.in_features
model_ft_scratch.fc = nn.Linear(num_ftrs, len(class_names)) # задаем 3 класса на выходе
model_ft_scratch = model_ft_scratch.to(device)

criterion = nn.CrossEntropyLoss() # Задаем функцию потерь

optimizer_ft_scratch = optim.SGD(model_ft_scratch.parameters(), lr=0.001, momentum=0.9)
exp_lr_scheduler_scratch = lr_scheduler.StepLR(optimizer_ft_scratch, step_size=7, gamma=0.1)

# Запускаем обучение на 5 эпох
print("Training ResNet-18 from scratch")
model_ft_scratch = train_model(model_ft_scratch, criterion, optimizer_ft_scratch, exp_lr_scheduler_scratch, num_epochs=5)

# Задаем предобученную на ImageNet модель.
model_ft_pretrained = models.resnet18(weights='IMAGENET1K_V1')

# Замораживаем все слои модели
for param in model_ft_pretrained.parameters():
    param.requires_grad = False

num_ftrs = model_ft_pretrained.fc.in_features
model_ft_pretrained.fc = nn.Linear(num_ftrs, len(class_names)) # При перезаписи, новый слой будет "разморожен"
model_ft_pretrained = model_ft_pretrained.to(device) # Отправляем на GPU

# Указываем оптимизатору, что только последний слой надо обновлять
optimizer_ft_pretrained = optim.SGD(model_ft_pretrained.fc.parameters(), lr=0.001, momentum=0.9)

exp_lr_scheduler_pretrained = lr_scheduler.StepLR(optimizer_ft_pretrained, step_size=7, gamma=0.1)

# Запускаем обучение на 5 эпох
print("Fine-tuning pretrained ResNet-18")
model_ft_pretrained = train_model(model_ft_pretrained, criterion, optimizer_ft_pretrained, exp_lr_scheduler_pretrained, num_epochs=5)

import torch
from torchvision import transforms
from PIL import Image
from google.colab import files

# Function to load and preprocess an image
def process_image(image_path):
    # Define preprocessing steps
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize to match the input size of ResNet-18
        transforms.ToTensor(),          # Convert PIL image to PyTorch tensor
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # Normalization
    ])

    # Load the image
    image = Image.open(image_path).convert('RGB')

    # Apply preprocessing
    image = preprocess(image)

    # Add a batch dimension (batch size of 1)
    image = image.unsqueeze(0)

    return image

# Function to make predictions on a single image
def predict_image(model, image_path):
    model.eval()  # Set model to evaluation mode

    # Load and preprocess the image
    image = process_image(image_path)

    # Move image to the same device as the model
    image = image.to(device)

    # Make the prediction
    with torch.no_grad():
        output = model(image)

    # Get the predicted class index
    _, predicted_idx = torch.max(output, 1)

    # Convert index to class name
    predicted_class = class_names[predicted_idx.item()]

    return predicted_class

# Loop to upload and predict multiple images
uploaded_files = files.upload()  # Upload files

for file_name in uploaded_files.keys():
    # predicted_class = predict_image(model_ft_scratch, file_name)
    predicted_class = predict_image(model_ft_pretrained, file_name)
    print(f'The predicted class for {file_name} is: {predicted_class}')

"""# Выводы

### Обучение с нуля:

Время: 8m 51s

Best val Acc: 0.7794

### Дообучение:

Время: 7m 47s

Best val Acc: 0.9856
"""