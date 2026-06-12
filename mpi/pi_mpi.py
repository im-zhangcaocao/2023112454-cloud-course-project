from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 10_000_000
local_n = N // size
start = rank * local_n
end = start + local_n if rank != size - 1 else N

h = 1.0 / N
local_sum = 0.0

t0 = time.time()
for i in range(start, end):
    x = h * (i + 0.5)
    local_sum += 4.0 / (1.0 + x * x)
elapsed = time.time() - t0

pi_local = local_sum * h

# MPI_Reduce: 将所有进程的 local_sum 归约求和到 root=0 进程
# 数据流向: 各进程 local_sum → (MPI_SUM) → root=0 进程的 global_sum
global_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

if rank == 0:
    pi = global_sum * h
    print(f"估算的 pi 值: {pi:.12f}")
    print(f"实际 pi 值:   {np.pi:.12f}")
    print(f"误差:         {abs(pi - np.pi):.2e}")
    print(f"进程数:       {size}")
    print(f"总点数:       {N}")
    print(f"计算耗时:     {elapsed:.4f}s (仅计算部分)")

# MPI_Barrier: 同步所有进程，确保各进程完成各自工作后才汇总
comm.Barrier()
if rank == 0:
    print(f"总耗时:       {time.time() - t0 + elapsed:.4f}s (含通信)")
    print("作业完成。")