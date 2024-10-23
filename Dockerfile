FROM public.ecr.aws/lambda/python:3.9

# Install Selenium and Chrome Driver
RUN yum install -y unzip \
    && pip install selenium webdriver-manager boto3

# Install Chrome browser
RUN curl -O https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm \
    && yum localinstall -y google-chrome-stable_current_x86_64.rpm

# Copy the dependencies to the Lambda Layer folder
RUN mkdir -p /opt/python \
    && pip install selenium webdriver-manager -t /opt/python

CMD ["lambda_function.lambda_handler"]
