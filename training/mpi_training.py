



from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
user_name = "Florian"


def min_and_max(list):
    min_element = min(list)
    max_element = max(list)
    return min_element, max_element



all_lists = []
for i in range(5):
    internal_list = []
    for j in range(i*10, i * 10 + 20, 2):
        internal_list.append(j)
    all_lists.append(internal_list)






if rank == 0:
    tasks = all_lists
    name = user_name

else: 
    tasks = None
    name = None


name_of_user = comm.bcast(name, root=0)

my_task = comm.scatter(tasks, root=0)


if rank != 0: 
    print(f"Rank {rank}: Recived task: {my_task}")


worker_result = min_and_max(my_task)

answer = {"message": f"Here is your result {name_of_user}", 
          "result": worker_result}


all_results = comm.gather(answer, root=0)


if rank == 0: 
    print(f"I am the master and i gathered these results")
    print(f"{all_results}")
else: 
    print("I am a worker and now have this: ", all_results)




