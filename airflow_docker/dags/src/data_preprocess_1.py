import pandas as pd
import cv2
import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa
import matplotlib.pyplot as plt


def preprocess_3(data_path, lables_path):
        
    try:

        # Load the image array and labels from the data_path
        image_array = np.load(data_path)
        print(image_array)
        labels_array = np.load(lables_path)

        # OpenCV reads images in BGR format by default when using cv2.imread()
        # Few libraries like matplotlib and PIL expects image in rgb format, so converting the image to bgr format
        image_rgb = []
        for img in image_array:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image_rgb.append(image)

        # converting the list to array
        images_array_rgb = np.array(image_rgb)
        
       
        # Define augmentation sequence (replace with your desired transformations)
        seq = iaa.Sequential([
            iaa.Fliplr(0.5),  # Flip horizontally with 50% probability
            iaa.Rotate((-10, 10)),  # Rotate between -10 and 10 degrees
            iaa.Crop(percent=(0.0, 0.1))  # Randomly crop up to 10% of the image
        ])

        # Augment the images
        augmented_images = seq(images=images_array_rgb)
        print(len(augmented_images))
        # img_to_plot = augmented_images[0]
        # plt.imshow(img_to_plot)
        # plt.show()

        # Append augmented images and labels to originals (assuming labels have the same order as images)
        augmented_images = np.concatenate((images_array_rgb, augmented_images))
        augmented_labels = np.concatenate((labels_array, labels_array.copy()))  # Duplicate labels for augmented images

        return augmented_images, augmented_labels, 200
     
    except ValueError as e:
        return {'error': f'{str(e)} - Invalid input'}, {'error': f'{str(e)} - Invalid input'}, 400
    
def preprocess_4(data_path):
        
    try:

        # Load the image array from the data_path
        image_array = np.load(data_path)

        # Normalization
        
        image_norm = (image_array/255).astype('float32')
        print('------- Shape and max/min values of the image after normalizing -------')
        print(image_norm.shape)
        print(image_norm.max(), image_norm.min())

        # Standardization

        mean = np.mean(image_array, axis=(0,1,2), keepdims=True)
        std = np.std(image_array, axis=(0,1,2), keepdims=True)
        image_std = (image_array - mean) / std
        print('------- Shape and max/min values of the image after standardizing -------')
        print(image_std.shape)
        print(image_std.max(), image_std.min())

        return image_norm, image_std, 200  
            
    except ValueError as e:
        return {'error': f'{str(e)} - Invalid input'}, {'error': f'{str(e)} - Invalid input'}, 400