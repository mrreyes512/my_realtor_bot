import argparse
import glob
import logging
import pendulum
import os, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

now = pendulum.now().format('%Y-%m-%d')

log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s | %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
    )

def call_chat_gpt(prompt, target_content):
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"{prompt}\n\n{target_content}",
        max_tokens=150
    )
    return response.choices[0].text.strip()

def find_cma_file(directory):
    search_pattern = os.path.join(f"files/{directory}", '*CMA.md')
    files = glob.glob(search_pattern)
    if files:
        return files[0]  # Return the first match
    else:
        return None

def get_questions():
    questions = [
        "What is the current market value of the property?",
        "What are the recent sales in the area?",
        "What are the key features of the property?",
        "What is the average price per square foot in the neighborhood?",
        "What are the market trends in the area?"
    ]
    return questions

def main(args):
    prompt_file = f"prompts/{args.prompt_file}.txt"
    target_file = find_cma_file(args.dir)

    log.info(f'Using prompt file: {prompt_file}')
    log.info(f'Using target file: {target_file}')

    try:
        with open(prompt_file, 'r') as file:
            prompt = file.read()
    except (FileNotFoundError, IOError) as e:
        log.error(f"Cannot read prompt file: {prompt_file} - {e}")
        return

    try:
        with open(target_file, 'r') as file:
            target_content = file.read()
    except (FileNotFoundError, IOError) as e:
        log.error(f"Cannot read target file: {target_file} - {e}")
        return

    questions = get_questions()
    responses = []
    for question in questions:
        response = call_chat_gpt(f"{prompt}\n\n{question}", target_content)
        log.info(f"ChatGPT Response for '{question}': {response}")
        responses.append(f"Question: {question}\nResponse: {response}\n")

    analysis_file = os.path.join(os.path.dirname(target_file), "AI_analysis.md")
    with open(analysis_file, 'w') as file:
        file.write("\n".join(responses))
    log.info(f"Responses saved to {analysis_file}")

if __name__ == "__main__":

    date = pendulum.now().to_date_string()

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-p', '--prompt_file', type=str, help="Path to the prompt text file")
    parser.add_argument('-d', '--dir', type=str, help="Path to the file to be analyzed")
    parser.add_argument('-q', '--question', type=str, help="Question to be asked")
    args = parser.parse_args()

    if args.v:
        logging.getLogger().setLevel(logging.INFO)
    log.info(f'{ "="*20 } Starting Script: { os.path.basename(__file__) } { "="*20 }')

    main(parser.parse_args())
