# Template-wizard with Docker

Template-wizard is a web application built with Streamlit that uses AI to analyze user-provided website URLs and suggest email templates based on the website's design and writing style. This README explains how to run the application using Docker.

## Getting Started

1. Clone the repository:

   ```shell
   git clone https://github.com/sonduong305/template-wizard.git
   ```

2. Navigate to the project directory:

   ```shell
   cd template-wizard
   ```

3. Build and run the Docker container:

   ```shell
   docker-compose up --build
   ```

Your Streamlit app will be accessible at `http://localhost:8501` in your web browser.

## Using Docker

We've simplified the setup by using Docker. Docker takes care of managing dependencies and running the app in a container. You don't need to worry about installing dependencies manually.

## Customization and Data

You can customize the app by modifying the contents the project's root directory. Any changes made to this directory will be reflected in the app running inside the Docker container.
