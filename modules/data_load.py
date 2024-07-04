from google.cloud import storage
import pandas as pd


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)

    # Note: The call returns a response only when the iterator is consumed.
    file_list = [blob.name for blob in blobs]
    # print(file_list)
    return file_list


def extract_exam_name(full_name):
    """
    Compose pretty exam name from json file name
    file_name: xxx_yyy_111.json
    exam_name: XXX (Yyy, 111)
    """
    # Exclude extension behind dot
    file_name = full_name.split('.')[0]
    parts = file_name.split('_')
    if len(parts) == 3:
        topic = parts[0].upper()
    else:
        topic = f"{parts[0].title()} {parts[1].upper()}"
    difficulty = parts[-2].title()
    size = parts[-1]
    exam_name = f"{topic} ({difficulty}, {size})"
    return exam_name


def compose_data(bucket_name, blob_file):
    file_path = f"gs://{bucket_name}/{blob_file}"
    question_data = pd.read_json(file_path)
    # Complete data, shuffle rows, reset index
    # question_data = question_data.sample(frac=1).reset_index(drop=True)
    # Pick multiple answers only
    # mask = question_data['correct_1'] == question_data['correct_1']
    # question_data = question_data[mask]
    return question_data


def combine_file_name(exam_name, size):
    """
    Convert exam name to json file name
    exam_name: XXX (Yyy, 111)
    file_name: xxx_yyy_111.json
    """
    parts = exam_name.split()
    if len(parts) == 3:
        # Convert to lowercase
        topic = f"failed_{parts[0].lower()}"
    else:
        topic = f"{parts[0]}_{parts[1]}".lower()
    # Exclude '(' and ','
    difficulty = parts[-2][1:-1].lower()
    file_name = f"{topic}_{difficulty}_{size}.json"
    return file_name
