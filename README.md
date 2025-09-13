# Cold Email Generator # AI Cold Email Generator

A professional cold email generator that helps you create personalized emails for job applications based on job postings.A Streamlit application that generates personalized cold emails for job applications by analyzing job postings using AI.

## Features## Features

- Automatically extracts job information from posting URLs- Extracts job information from any job posting URL

- Generates personalized cold emails using AI- Generates personalized cold emails based on job requirements

- Provides a user-friendly interface- Handles various job posting website formats

- Includes copy to clipboard functionality- Provides a user-friendly web interface

- Shows detailed job analysis

## Setup

- Python 3.10 or higher

1. Clone the repository:- Groq API key (sign up at https://console.groq.com)

````bash

git clone https://github.com/Iliyas-Pathan-19/cold-email-generator.git## Installation

cd cold-email-generator

```1. Clone the repository:



2. Create a virtual environment and activate it:

python/py -m venv venv

# On Windows:   ```

.\venv\Scripts\activate

# On Unix/MacOS:2. Create and activate a virtual environment:

source venv/bin/activate

```   ```bash

   # On Windows

3. Install dependencies:   py -m venv venv

                           .\venv\Scripts\activate

                           py -m pip install -r requirements.txt

```   # On macOS/Linux

##   python -m venv venv

4. Set up environment variables:   source venv/bin/activate

   - Copy `.env.example` to `.env`   ```

   - Add your Groq API key to `.env`

3. Install the required packages:

5. Run the application:

py -m pip install -r requirements.txt

streamlit run src/app.py

5. Open your web browser and go to http://localhost:8501

## Usage4. Create a `.env` file in the project root and add your Groq API key:

````

1. Enter a job posting URL GROQ_API_KEY=your_api_key_here

2. Click "Generate Email" ```

3. Review the job analysis

4. Use the generated email as a template## Usage

5. Always personalize before sending!

6. Start the application:

## Security Note

```bash

Never commit your actual `.env` file or API keys. Use `.env.example` as a template and keep your actual API keys secure.   streamlit run src/app.py
```

2. Open your web browser and go to http://localhost:8501

3. Enter a job posting URL in the input field

4. Click "Generate Email" to create a personalized cold email