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


def compose_data(bucket_name, blob_file):
    file_path = f"gs://{bucket_name}/{blob_file}"
    question_data = pd.read_json(file_path)
    # Complete data, shuffle rows, reset index
    # question_data = question_data.sample(frac=1).reset_index(drop=True)
    # Pick multiple answers only
    # mask = question_data['correct_1'] == question_data['correct_1']
    # question_data = question_data[mask]
    return question_data
