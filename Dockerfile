# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js, npm, openssh-client, and AWS CLI dependencies
RUN apt-get update && apt-get install -y nodejs npm openssh-client curl unzip

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
  unzip awscliv2.zip && \
  ./aws/install && \
  rm -rf aws awscliv2.zip

# Install Serverless Framework globally (version 3)
RUN npm install -g serverless@3

# Install Serverless Python Requirements plugin
RUN npm install --save-dev serverless-python-requirements

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Create .aws directory
RUN mkdir -p /root/.aws

# Copy AWS credentials from host
COPY .aws_credentials /root/.aws/credentials

# Keep the container running
CMD ["tail", "-f", "/dev/null"]