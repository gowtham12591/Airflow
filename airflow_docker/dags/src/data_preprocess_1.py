import pandas as pd
import cv2
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np



def image_preprocess_1(df_1, df_2):
        
    try:

        # Merging the dataframes
        merged_df = pd.merge(df_1, df_2, on='file_name')
        print('----- Checking merged dataframes information -------')
        print(merged_df.sample(5))
        print(len(merged_df))

        # Checking for null values in the merged dataframe, if there are any null values removing the particular row/image featires
        for col in merged_df.columns:
            if merged_df[col].isnull().any():
                merged_df.dropna(how='any', inplace=True)

        # splitting dataset to train and test
        # Define the class label column name (replace with your actual column name)
        class_label = "class"

        # Create a StratifiedShuffleSplit object
        sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)  # Adjust test_size as needed

        # Split the data into train and test sets (assuming your data is in a pandas DataFrame called df)
        for train_index, test_index in sss.split(merged_df, merged_df[class_label]):
            train_dataset = merged_df.iloc[train_index]
            test_dataset = merged_df.iloc[test_index]
        
        print('----- Checking the size of dataframes after splitting ------')
        print(len(train_dataset), len(test_dataset))

        # Reshaping train dataset suitable for the model
        # For reshaping the image, we can do it if it is in the form of an array or liost

        image_list = []
        resized_image_size = (128, 128)     # The image size can be dependent on the model
        image = train_dataset['image']
        label = train_dataset['class']

        for i, j in enumerate(image):
            img = cv2.resize(j, resized_image_size)      
            image_list.append(img)

        print('------ Images size after resizing as per the model requriement -------')
        print(len(image_list))

        # converting the list to array
        image_array = np.array(image_rgb)
        print('------- Shape of the image after reshaping -------')
        print(image_array.shape)

        # OpenCV reads images in BGR format by default when using cv2.imread()
        # Few libraries like matplotlib and PIL expects image in 
        image_rgb = []
        for img in image_list:
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image_rgb.append(image)

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

        return image_norm, 200
    
    except ValueError as e:
        return {'error': f'{str(e)} - Invalid input'}, 400