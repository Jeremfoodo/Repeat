import gdown

def download_excel_file(url, output):
    gdown.download(url, output, quiet=False)
