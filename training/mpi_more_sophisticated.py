


# from mpi4py import MPI
import cv2



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


from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


if rank == 0: 
    print("I am the master")











