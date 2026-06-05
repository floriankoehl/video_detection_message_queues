
# Write a function extract_frames(video_path) that:

# Opens data/video2.mp4
# Extracts all frames into a list
# Prints total frame count, fps, width and height
# Returns (frames, fps, width, height)

# Then write a second function reconstruct_video(frames, output_path, fps, width, height) 
# that takes that list of frames and writes them back to a new video file unchanged. 
# Verify the output video is playable.



import cv2
from ultralytics import YOLO


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

    return {
        "frames": frames, 
        "data": video_data
    }



model = YOLO("yolov8n.pt")

def run_detection(frame):
    raw_result = model(frame)[0]
    plotted_frame = raw_result.plot()

    detections = []
    for box in raw_result.boxes:
        detections.append({
            "label": raw_result.names[int(box.cls)],
            "confidence": float(box.conf),
            "bbox": box.xyxy[0].tolist()
        })


    return plotted_frame, detections









def reconstruct_video(frames, output_path, fps, width, height):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames: 
        output.write(frame)
    
    output.release()









def pipeline(video_path, output_path):
    video = extract_video_data(video_path)

    processed_frames = []
    for frame in video["frames"]:
        plotted_frame = run_detection(frame)
        processed_frames.append(plotted_frame)

    reconstruct_video(frames=processed_frames, 
                      output_path=output_path, 
                      fps=video["data"]["fps"], 
                      width=video["data"]["width"], 
                      height=video["data"]["height"])



pipeline("../data/video2.mp4", "../output_tests/reconstructed_video.mp4")




