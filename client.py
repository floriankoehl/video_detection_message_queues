import requests
import json
import time


PORT = 8000
URL = f"http://localhost:{PORT}"



def push_to_transactions(message):
    response = requests.post(f"{URL}/queues/transactions/messages", json=message).json()
    print(response)

def build_message(job_id, video_path):
    return {
            "job_id": job_id,
            "video": video_path
            }

def pop_from_results():
    response = requests.get(f"{URL}/queues/results/messages")

    if response.status_code == 200: 
        data = response.json()
        print("POPPED SUCESFULLY: ", data)
        return data
    else: 
        time.sleep(1)



if __name__ == "__main__":
    message = build_message(1, "data/video2.mp4")
    push_to_transactions(message)

    while True: 
        try:
            result = pop_from_results()
            print("sucesfully received the result!!!")
        except Exception as e: 
            print(str(e))
            break







