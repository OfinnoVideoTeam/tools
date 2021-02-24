# It's for Ubuntu EC2
# This script performs
# 1. mount s3 bucket whose name is buck_name to folder_name
# 2. install aws commandline package
# You need to know ACCESS_KEY_ID and SECRET_ACCESS_KEY of your aws account (please ask Dan)
# And replace "input your aws_access_key_id" and "input your aws_secret_access_key" with yours.
# you can find available s3 buckets using the following command
# aws s3 ls

sudo apt upgrade
sudo apt update
sudo apt install s3fs
sudo apt install awscli

#list s3 bucket list

ACCESS_KEY_ID="input your aws_access_key_id"
SECRET_ACCESS_KEY="input your aws_secret_access_key"

mkdir .aws
echo "[default]\nregion=us-east-1\noutput=json " > .aws/config
echo "[default]\naws_access_key_id=${ACCESS_KEY_ID}\naws_secret_access_key=${SECRET_ACCESS_KEY}" > .aws/credentials

#aws s3 ls 

echo ${ACCESS_KEY_ID}:${SECRET_ACCESS_KEY} > ${HOME}/.passwd-s3fs
chmod 600 .passwd-s3fs

mkdir folder_name # you can change folder_name to any name

s3fs bucket_name ./folder_name -o passwd_file=${HOME}/.passwd-s3fs 
