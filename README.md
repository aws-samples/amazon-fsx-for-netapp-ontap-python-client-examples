## Amazon FSx for NetApp ONTAP - serverless file serving - Python client library examples

This repository contains examples for using the [NetApp ONTAP Python client library](https://docs.netapp.com/us-en/ontap-automation/python/overview_pcl.html) for serving files and browsing file listings in an [Amazon FSx for NetApp ONTAP](https://aws.amazon.com/fsx/netapp-ontap/) file system.  These will run in a serverless fashion using an [AWS Lambda](https://aws.amazon.com/lambda/) function.

### Overview

[Amazon FSx for NetApp ONTAP](https://aws.amazon.com/fsx/netapp-ontap/) is a fully managed service that provides highly reliable, scalable, high-performing and feature-rich file storage built on NetApp's popular ONTAP file system.  It supports access using the Network File System (NFS) protocol (v3, v4.0, v4.1 and v4.2), all versions of the Server Message Block (SMB) protocol (including 2.0, 3.0, and 3.1.1) and the Internet Small Computer Systems Interface (iSCSI) protocol.  These mechanisms can be used to read/write files from an EC2 instance, ECS/EKS containers etc.  The preferred way of using these is to mount the file system to the respective compute instance/container.  In addition to these, NetApp ONTAP also provides a [Python client library](https://docs.netapp.com/us-en/ontap-automation/python/overview_pcl.html) to interact with the file system.  This library is a Python wrapper over a [REST API](https://library.netapp.com/ecmdocs/ECMLP2856304/html/index.html).  Using this mechanism, applications can read/write files using the light-weight APIs and without mounting the file system in their environment.  This provides an easy way to share files/content between Virtual Machines, bare metal machines, containers and serverless applications.  Typical use cases for serverless applications to use this file system will be to serve content for websites, provide file download and sharing capabilities and to enable the migration of applications to serverless environments without changing the backed storage system.

In this context, the samples provided here are will run in an [AWS Lambda](https://aws.amazon.com/lambda/) function.

Note that this API currently supports a max size of 1 MB for reading and writing files.

### Repository structure

This repository contains the following directories,

* [src](https://github.com/aws-samples/amazon-fsx-for-netapp-ontap-python-client-examples/tree/main/src) - the Python source file for the sample Lambda function.

### Prerequisites to run the examples

Prior to running these examples, make sure you have all the following components configured in the same AWS account, in the same AWS region and in the same VPC.

**Amazon FSx for NetApp ONTAP - File System and Storage Virtual Machine:**

1. Create a security group with a self-refencing rule for all ports and protocols.
2. Create a NetApp ONTAP FSx file system with at least one volume (not including the root volume).  Make sure to use the security group created in the previous step.  Also, make sure you specify a password.
3. Create a Storage Virtual Machine (SVM) for the file system created in the previous step.  Also, make sure you specify a password.

**Amazon EC2 instance:**

In this sample, this EC2 instance will create a file which will then be read by the Lambda function.  This will show how files can be shared between these services.

1. Create an Amazon EC2 instance in the same VPC as the NetApp ONTAP FSx file system.
2. Now, take the private IP address of this instance and add it to the security group of the FSx file system created earlier.  Make sure to include all ports and protocols as specified [here](https://docs.netapp.com/us-en/cloud-manager-fsx-ontap/requirements/reference-security-groups-fsx.html#rules-for-fsx-for-ontap).
3. Mount the volume created earlier onto the EC2 instance.  For instructions, refer [here](https://docs.aws.amazon.com/fsx/latest/ONTAPGuide/attach-volumes.html).
4. On that volume, create a file with some content.  Example: *file1.txt*.

**AWS Lambda function:**

1. Create a Lambda layer to package the Python module [netapp-ontap](https://github.com/NetApp/ontap-rest-python) as a dependency.

    a. Create a folder with a name you prefer.  We have used 'netapp-ontap-layer' here.

    b. Inside this folder, create a folder named 'python'.  This should be the exact name and Lambda will unpack the contents of this folder.

    c. Inside the 'python' folder, run the following command to install the required libs.  In our case, we are are installing the latest version of 'netapp-ontap'.

        pip install netapp-ontap -t ./

    d. Now *cd* out of that folder back to 'netapp-ontap-layer' and zip the contents of the 'python' folder to a file named 'netapp-ontap-layer.zip'.

    e. In the Lambda console, create a custom layer named 'netapp-ontap-layer' and upload this zip file to it.

2. Create a Python 3.9 Lambda function with the following,

    a. Specify the same VPC as used as the FSx file system.

    b. Attach the security group of the FSx file system.

    c. Specify an IAM role with the appropriate permissions to write to [Amazon CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html) and other services as required.

    d. Attach the Lambda layer 'netapp-ontap-layer' created above.

    e. Set the memory to at least 1 GB and a timeout value of at least 30 seconds.

    f. There is no need to attach a trigger as we will be running this function manually in this sample.

    g. Copy the code found in the `src` folder into the function.
3. Specify the following configuration as environment properties in the function.  Note that in an actual implementation, it is recommended to use the [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html) for storing these configuration properties.  Secrets are recommended to be stored in the [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html).

    a. *LOG_LEVEL* - specifies the logging level of the function.  Valid values are NOTSET, DEBUG, INFO, WARNING, ERROR and CRITICAL.  For running this sample, DEBUG level should be appropriate.

    b. *FSX_ONTAP_FS_DNS_NAME* - the DNS name of the FSx file system's management endpoint.

    c. *FSX_ONTAP_FS_USER_NAME* - the username of the FSx file system's management endpoint.  This should be 'fsxadmin'.

    d. *FSX_ONTAP_FS_PASSWORD* - the password of the FSx file system's management endpoint.

    e. *FSX_ONTAP_SVM_NAME* - the name of the Storage Virtual Machine.

    f. *FSX_ONTAP_VOLUME_UUID* - the UUID of the volume from which the file will be served.  Make sure this is the same as the volume in which the EC2 instance writes the file.

### How to run the examples

1. Create the following test event in the Lambda test console.  Specify the path to the file from the root directory of the file system.  Make sure this is the same file that is created by the EC2 instance.  Do not add a leading '/' to the file path.  Example: *file1.txt*.

  *{"file_name_with_path": "file1.txt"}*

2. Using this test event, run the Lambda function and observe the output in the Lambda test console.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

