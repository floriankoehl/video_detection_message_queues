
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from message_queue import MessageQueueManager
import uvicorn
import threading
import time
import json




with open("config.json") as f:
    config = json.load(f)


app = FastAPI()
manager = MessageQueueManager()
manager.load()

def persist_loop():
    while True:
        time.sleep(config["persistence_interval"])
        manager.save()

threading.Thread(target=persist_loop, daemon=True).start()






# Endpoints
@app.get("/health")
def health_check():
    return {"message": "healthy!"}

@app.post("/queues/{name}")
def create_queue(name: str):
    try: 
        manager.create_queue(name)
        return {"message": "Queue sucesfully created!"}
    except Exception as e: 
        return JSONResponse(
            status_code=409,
            content={"error": str(e)}
        )

@app.delete("/queues/{name}")
def delete_queue(name: str):
    try: 
        manager.delete_queue(name)
        return {"message": "Queue deleted sucesfully!"}
    except Exception as e: 
        return JSONResponse(
            status_code=409,
            content={"error": str(e)}
        )

@app.get("/queues")
def list_queues():
    try: 
        queues = manager.list_queues()
        return list(queues)
    except Exception as e: 
        return JSONResponse(
            status_code=409,
            content={"error": str(e)}
        )

@app.post("/queues/{name}/messages")
def push_to_queue(name: str, message: dict = Body(...)):
    try:
        manager.push(name, message)
        return {"message": "Message added successfully to queue!"}
    except Exception as e:
        return JSONResponse(
            status_code=409,
            content={"error": str(e)}
        )

@app.get("/queues/{name}/messages")
def pop_from_queue(name: str):
    try: 
        return manager.pop(name)
    except Exception as e: 
        return JSONResponse(
            status_code=409,
            content={"error": str(e)}
        )

@app.get("/get_queue_content/{name}")
def get_queue_content(name: str):
    try: 
        messages = manager.get_queue_content(name)
        return {"messages": messages}
    except Exception as e: 
        return JSONResponse(
            status_code=409,
            content={"error": str(e)}
        )










if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






