import pandas as pd



def image_preprocess_1(df_1, df_2):

    merged_df = pd.merge(df_1, df_2, on='file_name')
    print(merged_df.sample(5))

    


    return merged_df