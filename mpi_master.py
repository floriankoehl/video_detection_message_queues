# from mpi4py import MPI
import cv2
from ultralytics import YOLO
from mpi4py import MPI
import numpy as np
import os
import requests
import time


PORT = 8000
URL = f"http://localhost:{PORT}"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

model = YOLO("yolov8n.pt")




# ----------------------------
# Initalize Queue
# ----------------------------
def create_transaction_queue():
    response = requests.post(f"{URL}/queues/transactions").json()
    print(response)

def create_result_queue():
    response = requests.post(f"{URL}/queues/results").json()
    print(response)

def initalize_queue():
    create_transaction_queue()
    create_result_queue()











# ----------------------------
# Process video
# ----------------------------
def extract_metadata(video):
    return {
        "fps": video.get(cv2.CAP_PROP_FPS),
        "width": int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "total_frames": video.get(cv2.CAP_PROP_FRAME_COUNT)
    }

def extract_frames(video):
    frames = []
    while True: 
        is_read, frame = video.read()
        if not is_read:
            print("Video ended")
            break
        frames.append(frame)
    
    return frames

def extract_video_data(video_path: str) -> list:
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("could not open video")

    video_data = extract_metadata(video)
    frames = extract_frames(video)
    
    video.release()

    return frames, video_data

def reconstruct_video(frames, output_path, fps, width, height):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames: 
        output.write(frame)
    output.release()

def run_detection(frame):
    raw_result = model(frame)[0]
    plotted_result = raw_result.plot()

    detections = []
    if raw_result.boxes is not None:
        for box in raw_result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            bbox = box.xyxy[0].tolist()

            detections.append({
                "label": raw_result.names[class_id],
                "confidence": confidence,
                "bbox": bbox
            })

    return plotted_result, detections

def flatten_frames_from_chunks(chunks):
    all_frames = []
    for chunk in chunks:
        all_frames.extend(chunk)
    return all_frames

# ----------------------------
# MPI PART
# ----------------------------


if rank == 0:
    initalize_queue()
comm.barrier()

while True:


    # Pop Jobs
    if rank == 0: 
        response = requests.get(f"{URL}/queues/transactions/messages")
        if response.status_code == 200: 
            job = response.json()
            print(job)
        else: 
            job = None
    else: 
        job = None

    job = comm.bcast(job, root=0)

    if job is None:
        time.sleep(1)
        continue



    # Define Jobs
    if rank == 0: 
        frames, video_data = extract_video_data(job["video"])
        chunks = np.array_split(frames, size)

    else: 
        chunks = None
        video_data = None



    # Scatter the Data
    frames = comm.scatter(chunks, root=0)



    # Run the computation
    os.makedirs(f"output/worker_{rank}", exist_ok=True)
    results = []
    for i, frame in enumerate(frames): 
        plottet_frame, detections = run_detection(frame)
        cv2.imwrite(f"output/worker_{rank}/frame_{i}.jpg", plottet_frame)
        results.append(plottet_frame)


    # Gather the results
    all_frames_chunks = comm.gather(results, root=0)


    # Reconstruct the video
    if rank == 0: 
        all_frames = flatten_frames_from_chunks(all_frames_chunks)
        reconstruct_video(
            frames=all_frames,
            output_path=f"output/result_{job['job_id']}.mp4",
            fps=video_data["fps"],
            width=video_data["width"],
            height=video_data["height"]
        )


        response = requests.post(f"{URL}/queues/results/messages",
                                 json={
                                     "job_id": job["job_id"],
                                     "output_video": f"output/result_{job['job_id']}.mp4"
                                 })


        if response.status_code == 200: 
            print("sucesfully returned result!")
        else: 
            print("Something went wrong when pushing to the queue")























# while True: 
#         job = requests.get(f"{URL}/queues/transactions/messages")
#         print("Received job: ", job)


