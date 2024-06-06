import os
import cv2
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit
import ast

dataset_path = "C:\\Users\\azureuser\\Documents\\airflow\\airflow_docker\\dags\\data"
storage_path = dataset_path + '\\preprocess'
data_path = storage_path + '\\' + 'image_data.csv'

# Read the dataframe from the path
df_image = pd.read_csv(data_path)
    
try:

    # Checking for null values in the merged dataframe, if there are any null values removing the particular row/image featires
    for col in df_image.columns:
        if df_image[col].isnull().any():
            df_image.dropna(how='any', inplace=True)

    # splitting dataset to train and test
    # Define the class label column name (replace with your actual column name)
    class_label = "class"

    # Create a StratifiedShuffleSplit object
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)  # Adjust test_size as needed

    # Split the data into train and test sets (assuming your data is in a pandas DataFrame called df)
    for train_index, test_index in sss.split(df_image, df_image[class_label]):
        train_dataset = df_image.iloc[train_index]
        test_dataset = df_image.iloc[test_index]

    print('----- Checking the size of dataframes after splitting ------')
    print(len(train_dataset), len(test_dataset))

    print(train_dataset.shape)

    print(type(train_dataset))

    print(train_dataset.head(5))

    var = train_dataset['image_path']
    print(type(var))

        # Reshaping train dataset suitable for the model
    # For reshaping the image, we can do it if it is in the form of an array or list
    image_list = []
    resized_image_size = (128, 128)     # The image size can be dependent on the model

    # Loop it and resize the image
    for index, img in enumerate(train_dataset['image_path']):
        # print(img)
        # img = np.array(ast.literal_eval(img))
        # print(type(img))
        # print(img)
        image = cv2.imread(img)  # Load the image using cv2.imread()
        resized_image = cv2.resize(image, resized_image_size)      
        image_list.append(resized_image)

    # Converting the images in list to array
    image_array = np.array(image_list)

    labels_list = []
    # Loop it and convert the label to list
    for index, label in enumerate(train_dataset['class']):      
        labels_list.append(label)

    label_array = np.array(labels_list)

    print(image_array, label_array, test_dataset, 200)   
        
except ValueError as e:
    print(f'error {str(e)}')
    
    