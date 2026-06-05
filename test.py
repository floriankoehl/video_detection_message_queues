import requests
import time
import uuid
import os

SERVER = "http://localhost:8000"

print("===================================")
print("A4 MPI + MQ Distributed System Test")
print("===================================\n")

# -----------------------------------
# Test 1: MQ server availability
# -----------------------------------

print("[TEST 1] Checking MQ server...")

try:
    r = requests.get(f"{SERVER}/queues")

    if r.status_code == 200:
        print("PASS: MQ server is running")
        print("Queues:", r.json())
    else:
        print("FAIL: MQ server error")

except Exception as e:
    print("FAIL: Cannot connect to MQ server")
    print(e)
    exit()

print()

# -----------------------------------
# Test 2: Submit video job
# -----------------------------------

print("[TEST 2] Submitting video job...")

job_id = str(uuid.uuid4())

video_path = "data/video2.mp4"

if not os.path.exists(video_path):
    print("FAIL: Test video not found")
    exit()

job = {
    "job_id": job_id,
    "video": video_path
}

try:

    r = requests.post(
        f"{SERVER}/queues/transactions/messages",
        json=job
    )

    if r.status_code == 200:
        print("PASS: Video job submitted")
        print("Job ID:", job_id)
    else:
        print("FAIL: Could not submit job")
        print(r.text)
        exit()

except Exception as e:
    print("FAIL:", e)
    exit()

print()

# -----------------------------------
# Test 3: Wait for processing result
# -----------------------------------

print("[TEST 3] Waiting for processing result...")

start_time = time.time()

output_video = None

while True:
    if time.time() - start_time > 400:
        print("FAIL: Timeout")
        exit()

    try:

        r = requests.get(
            f"{SERVER}/queues/results/messages"
        )

        data = r.json()

        if data.get("job_id") == job_id:

            output_video = data.get("output_video")

            print("PASS: Processing completed")
            print("Output:", output_video)

            break

    except Exception as e:
        print("Polling error:", e)

    time.sleep(2)

processing_time = time.time() - start_time

print()

# -----------------------------------
# Test 4: Validate output video
# -----------------------------------

print("[TEST 4] Validating output video...")

if output_video and os.path.exists(output_video):

    print("PASS: Output video exists")

    file_size = os.path.getsize(output_video)

    print("Video size:", file_size, "bytes")

    if file_size > 0:
        print("PASS: Output video is not empty")
    else:
        print("FAIL: Output video is empty")

else:
    print("FAIL: Output video not found")

print()


# -----------------------------------
# Test 5: MPI worker distribution
# -----------------------------------

print("[TEST 5] Validating MPI worker distribution...")
output_dir = "output"
worker_frames = {}

for item in os.listdir(output_dir):

    if item.startswith("worker_"):

        worker_path = os.path.join(output_dir, item)

        frames = os.listdir(worker_path)

        worker_frames[item] = len(frames)

if len(worker_frames) > 1:

    print("PASS: Multiple MPI workers participated")

    for worker, count in worker_frames.items():
        print(worker, "processed", count, "frames")

else:
    print("FAIL: MPI distribution not detected")

print()



# -----------------------------------
# Test 6: Performance summary
# -----------------------------------

print("[TEST 6] Performance summary")

print(f"Total processing time: {processing_time:.2f} seconds")

print()

# -----------------------------------
# Final result
# -----------------------------------

print("===================================")
print("Testing completed")
print("===================================")
