# from mpi4py import MPI
import cv2
from ultralytics import YOLO
from mpi4py import MPI
import numpy as np



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


# ----------------------------
# Yolo Part
# ----------------------------
model = YOLO("yolov8n.pt")

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



# ----------------------------
# MPI PART
# ----------------------------
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


if rank == 0: 
    print(f"I am the master")
    frames, video_data = extract_video_data("../data/video2.mp4")
    chunks = np.array_split(frames, size)

else: 
    chunks = None
    video_data = None

# Video data broadcast for now not necessary but could be useful later
video_data = comm.bcast(video_data, root=0)
jobs = comm.scatter(chunks, root=0)




import os

os.makedirs(f"../output_tests/worker_{rank}", exist_ok=True)

results = []
for i, job in enumerate(jobs): 
    plottet_frame, detections = run_detection(job)
    cv2.imwrite(f"../output_tests/worker_{rank}/frame_{i}.jpg", plottet_frame)
    results.append(plottet_frame)



all_frames_chunks = comm.gather(results, root=0)


def reconstruct_video(frames, output_path, fps, width, height):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames: 
        output.write(frame)
    output.release()




if rank == 0: 
    all_frames = []
    for chunk in all_frames_chunks:
        all_frames.extend(chunk)


    reconstruct_video(
        frames=all_frames,
        output_path="../output_tests/reconstructed_video.mp4",
        fps=video_data["fps"],
        width=video_data["width"],
        height=video_data["height"]
    )













