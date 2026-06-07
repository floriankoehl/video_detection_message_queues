# Assignment 4: Distributed Video Analytics with MPI + MQ

Distributed YOLO video processing pipeline combining a Message Queue service for async client communication and MPI for parallel frame inference.

## Components

| File | Role |
|---|---|
| `server.py` | FastAPI MQ server with REST endpoints |
| `message_queue.py` | Thread-safe FIFO queue with persistence |
| `client.py` | Submits video jobs and retrieves results |
| `mpi_master.py` | MPI master/worker: scatters frames, runs YOLO, reconstructs video |
| `config.json` | Queue max size and persistence interval |

## How to Run

```bash
# 1. Start the MQ server
python server.py

# 2. Start the MPI processing service (5 processes: 1 master + 4 workers)
mpirun -np 5 python mpi_master.py

# 3. Submit a video job and retrieve the result
python client.py

# 4. Run the test suite
python test.py
```

## Workflow

1. Client pushes `{ job_id, video }` to the `transactions` queue
2. MPI master (rank 0) pops the job and extracts frames
3. Frames are scattered across MPI workers via `MPI.Scatter`
4. Each worker runs YOLO detection and saves annotated frames to `output/worker_<rank>/`
5. Results are gathered back to master via `MPI.Gather`
6. Master reconstructs the annotated video and pushes `{ job_id, output_video }` to the `results` queue
7. Client pops the result from the `results` queue

## Configuration (`config.json`)

```json
{ "max_size": 50, "persistence_interval": 5 }
```

- `max_size`: maximum messages per queue
- `persistence_interval`: seconds between queue snapshots to `queues.json`

## Output

- Annotated video: `output/result_<job_id>.mp4`
- Per-worker frames: `output/worker_<rank>/frame_<n>.jpg`
