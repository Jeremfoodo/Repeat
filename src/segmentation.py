import pandas as pd

def load_segmentation_data(file_path="segmentation_data.xlsx"):
    return pd.read_excel(file_path, engine='openpyxl')
