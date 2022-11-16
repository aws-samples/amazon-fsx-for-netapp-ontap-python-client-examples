"""
Copyright 2022 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
import json
import logging
import re
from netapp_ontap import HostConnection, NetAppRestError, config, utils
from netapp_ontap.resources import FileInfo, Volume


# Set the logger
def set_log_config(logger_obj):
    log_level = os.environ['LOG_LEVEL']
    if log_level.upper() == 'NOTSET':
        logger_obj.setLevel(logging.NOTSET)
    elif log_level.upper() == 'DEBUG':
        logger_obj.setLevel(logging.DEBUG)
        utils.DEBUG = 1
    elif log_level.upper() == 'INFO':
        logger_obj.setLevel(logging.INFO)
    elif log_level.upper() == 'WARNING':
        logger_obj.setLevel(logging.WARNING)
    elif log_level.upper() == 'ERROR':
        logger_obj.setLevel(logging.ERROR)
    elif log_level.upper() == 'CRITICAL':
        logger_obj.setLevel(logging.CRITICAL)
    else:
        logger_obj.setLevel(logging.NOTSET)


logger = logging.getLogger()
set_log_config(logger)


# Get the connection for specific requirements
def get_connection(connection_type):
    if connection_type == 'file_read_write':
        return HostConnection(os.environ['FSX_ONTAP_FS_DNS_NAME'],
                              username=os.environ['FSX_ONTAP_FS_USER_NAME'],
                              password=os.environ['FSX_ONTAP_FS_PASSWORD'],
                              verify=False,
                              headers={"Accept": "multipart/form-data"})
    else:
        return HostConnection(os.environ['FSX_ONTAP_FS_DNS_NAME'],
                              username=os.environ['FSX_ONTAP_FS_USER_NAME'],
                              password=os.environ['FSX_ONTAP_FS_PASSWORD'],
                              verify=False)


# Print the info of all volumes in the file system
def print_info_of_all_volumes(svm_name):
    volumes = Volume.get_collection(**{'svm.name': svm_name})
    logger.info('Volumes for SVM "{}"...'.format(svm_name))
    for index, volume in enumerate(volumes):
        logger.info('Volume {} :: name = "{}", uuid = "{}"'.format((index + 1),
                                                                       volume['name'], volume['uuid']))


# Print the info of all files in the root directory of all volumes in the file system
def print_info_of_root_dir_files_in_all_volumes(svm_name):
    volumes = Volume.get_collection(**{'svm.name': svm_name})
    logger.info('Volumes for SVM "{}"...'.format(svm_name))
    for index, volume in enumerate(volumes):
        logger.info('Volume {} :: name = "{}", uuid = "{}"'.format((index + 1),
                                                                       volume['name'], volume['uuid']))
        logger.info('Files for volume "{}"...'.format(volume['name']))
        file_info_resources = FileInfo.get_collection(volume['uuid'], '')
        for index1, file_info_resource in enumerate(file_info_resources):
            logger.info('File {} :: type = "{}", path = "{}", name = "{}"'.format((index1 + 1),
                                                                     file_info_resource['type'],
                                                                     file_info_resource['path'],
                                                                     file_info_resource['name']))


# Print the content of the specified file
def print_file_content(file_name_with_path):
    # Retrieve the file content - max size of 1 MB
    resource = FileInfo(os.environ['FSX_ONTAP_VOLUME_UUID'], file_name_with_path)
    file_read_response = resource.get(byte_offset=0, length=1023)
    if file_read_response.is_err:
        logger.error('Error occurred :: {}'.format(file_read_response))
    else:
        # Decode the NetApp ONTAP API response, parse, retrieve the file content and print it
        decoded_file_read_response = file_read_response.http_response.content.decode('utf-8')
        decoded_file_read_response = re.sub(r'\r', '', decoded_file_read_response)
        decoded_file_read_response_lines = decoded_file_read_response.split('\n')
        decoded_file_read_response_lines = list(filter(None, decoded_file_read_response_lines))
        decoded_file_read_response_lines_start_index = decoded_file_read_response_lines.\
            index('Content-Type: application/octet-stream') + 1
        decoded_file_read_response_lines_end_index = len(decoded_file_read_response_lines) - 1
        file_content_lines = decoded_file_read_response_lines[decoded_file_read_response_lines_start_index
                                                              :decoded_file_read_response_lines_end_index]
        file_content = '\n'.join(file_content_lines)
        logger.info('Content of file "{}" :: {}'.format(file_name_with_path, file_content))


# Lambda handler function
def lambda_handler(event, context):
    # Log the request
    logger.debug('REQUEST :: {}'.format(json.dumps(event, indent=2)))

    try:
        # Demo 1: List volumes and files
        # Get the connection
        connection = get_connection('volume_file_list')
        # Set connection as the default for all NetApp ONTAP API calls
        config.CONNECTION = connection
        # Print volume info
        print_info_of_all_volumes(os.environ['FSX_ONTAP_SVM_NAME'])
        # Print file info
        print_info_of_root_dir_files_in_all_volumes(os.environ['FSX_ONTAP_SVM_NAME'])

        # Demo 2: Read file from a volume
        # Get the connection
        connection = get_connection('file_read_write')
        # Set connection as the default for all NetApp ONTAP API calls
        config.CONNECTION = connection
        # Print file content
        print_file_content(event['file_name_with_path'])
    except NetAppRestError as error:
        logger.error('Error occurred :: {}'.format(error))

    # Log the response
    response = {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
    logger.debug('RESPONSE :: {}'.format(json.dumps(response, indent=2)))
    # Return the response
    return response
