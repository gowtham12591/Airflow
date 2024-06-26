import os
import cv2
import pandas as pd
    
# Extract the images

def image_extract(dataset_path):

    df = pd.DataFrame(columns=["file_name", "class", "image"])

    try:

        for labels in os.listdir(dataset_path + '/plant_images'):
            if labels != ".DS_Store":
                print(f"Processing class: {labels}")
                class_path = os.path.join(dataset_path + '/plant_images', labels)

                for img in os.listdir(class_path):
                    image_path = os.path.join(class_path, img)
                    image = cv2.imread(image_path)

                    # Temporary list to store data for each image
                    image_data = {"file_name": img, "class": labels, "image": image}

                    # Append data using pd.concat (recommended approach)
                    df = pd.concat([df, pd.DataFrame.from_dict([image_data])], ignore_index=True)

            # After processing all images, consider saving the DataFrame
        if len(df) > 0:
            # df.to_csv(dataset_path + "/preprocess_1/plant_image_data.csv", index=False)  # Save DataFrame as CSV
            df_postgres = df[['file_name', 'class']]
            df_minio = df[['file_name', 'image']]

            return df_postgres, df_minio, 200

        else:
            return {'message': 'Images not appended in dataframe'}, 406
    
    except ValueError as e:
        return {'error': f'{str(e)} - Invalid input. Please enter image size as width,height (e.g., 128, 128)'}, 400
        

    