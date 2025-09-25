# batch_status_printer.py
import os
from time import sleep as s
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prev_ops = None

while True:
    bids = [b.id for b in client.batches.list().data]
    ops = [f"{bid[-3:]}:{client.batches.retrieve(bid).status}" for bid in bids]

    # 상태 변경 확인
    if ops != prev_ops:
        os.system('cls' if os.name == 'nt' else 'clear')
        for i in ops:
            print(i)
        print("*" * 33)
        for i in bids:
            print(i)
        prev_ops = ops  # 최신 상태 저장

    s(3600)
    

