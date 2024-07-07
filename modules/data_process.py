from google.cloud import storage
import pandas as pd

from app import exam_list, exam_library


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
    """
    Turn JSON file in bucket into dataframe
    """
    file_path = f"gs://{bucket_name}/{blob_file}"
    question_data = pd.read_json(file_path)
    return question_data


def load_bucket(bucket):
    """
    List all blobs in bucket and return dataframe and exam name corresponding to each JSON file
    """
    e_list = []
    e_library = {}
    file_list = list_blobs(bucket)
    for full_name in file_list:
        if full_name.split('.')[-1] == 'json':
            exam_name = extract_exam_name(full_name)
            e_list.append(exam_name)
            e_library[exam_name] = compose_data(bucket, full_name).copy()
    return {'e_list': e_list,
            'e_library': e_library}


def load_exam(bucket):
    """
    By calling load_bucket(), files list from our bucket is updated
    Assigned those new data to current `exam_list` and `exam_library`
    """
    # Adjust value of global variables
    global exam_list, exam_library
    bucket_data = load_bucket(bucket)
    exam_list = bucket_data['e_list']
    exam_library = bucket_data['e_library']


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


def export_gcs(exam_library, exam_name, index_list, bucket):
    q_bank = exam_library[exam_name]
    failed_bank = q_bank.loc[index_list]
    size = len(index_list)
    filename = combine_file_name(exam_name, size)
    failed_bank.to_json(f"gs://{bucket}/{filename}")
