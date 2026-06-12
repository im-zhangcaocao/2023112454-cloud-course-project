from mpi4py import MPI
import numpy as np
import time
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 800


def matrix_mul_mpi():
    if rank == 0:
        np.random.seed(42)
        A = np.random.rand(N, N).astype(np.float64)
        B = np.random.rand(N, N).astype(np.float64)
    else:
        A = None
        B = None

    rows_per_proc = N // size
    local_A = np.empty((rows_per_proc, N), dtype=np.float64)

    comm.Scatter(A, local_A, root=0)
    B = comm.bcast(B, root=0)

    t_comp_start = time.time()
    local_C = local_A @ B
    t_comp_end = time.time()

    if rank == 0:
        C_mpi = np.empty((N, N), dtype=np.float64)
    else:
        C_mpi = None
    comm.Gather(local_C, C_mpi, root=0)

    return t_comp_end - t_comp_start


if rank == 0:
    print("=" * 60)
    print(f"MPI 性能测试 - 矩阵乘法 N={N}, P={size}")
    print("=" * 60)

comm.Barrier()
t0 = time.time()
comp_time = matrix_mul_mpi()
comm.Barrier()
total_time = time.time() - t0

if rank == 0:
    print(f"进程数: {size}")
    print(f"计算时间: {comp_time:.4f}s")
    print(f"总时间(含通信): {total_time:.4f}s")

    with open("mpi_perf_result.txt", "a") as f:
        f.write(f"{size},{comp_time},{total_time}\n")

    print("结果已记录到 mpi_perf_result.txt")