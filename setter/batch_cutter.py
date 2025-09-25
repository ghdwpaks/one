#run it like this.
#batch_cutter.py batch_68d38bdb97848190b46295042dea56f9
import os
import argparse
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description="Cancel an OpenAI batch job.")
    parser.add_argument("batch_id", help="The batch ID to cancel.")  # 위치 인자
    args = parser.parse_args()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.batches.cancel(args.batch_id)
    

if __name__ == "__main__":
    main()

