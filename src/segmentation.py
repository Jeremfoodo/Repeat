def load_segmentation_data():
    url = 'https://drive.google.com/uc?id=1lCVTDYtM_SWj1W5OqTr15-56K4BCWPqf'
    output = 'segmentation_data.xlsx'
    gdown.download(url, output, quiet=False)
    df = pd.read_excel(output, engine='openpyxl')
    return df
