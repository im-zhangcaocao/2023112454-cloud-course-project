from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 800

if rank == 0:
    print("=" * 60)
    print("MPI 并行矩阵乘法 - 阻塞通信版 (N={}, P={})".format(N, size))
    print("=" * 60)

    np.random.seed(42)
    A = np.random.rand(N, N).astype(np.float64)
    B = np.random.rand(N, N).astype(np.float64)
    t_start = time.time()
else:
    A = None
    B = None

rows_per_proc = N // size
local_A = np.empty((rows_per_proc, N), dtype=np.float64)

# MPI_Scatter: 将矩阵 A 按行均匀分发给所有进程
# 数据流向: root=0 持有完整 A → 每个进程获得 rows_per_proc 行
comm.Scatter(A, local_A, root=0)

# MPI_Bcast: 将矩阵 B 完整广播给所有进程
# 数据流向: root=0 → 所有进程收到完整 B
B = comm.bcast(B, root=0)

t_comp_start = time.time()
local_C = local_A @ B
t_comp_end = time.time()

local_comp_time = t_comp_end - t_comp_start

# MPI_Gather: 将所有进程的 local_C 收集回 root=0
# 数据流向: 各进程 local_C → root=0 进程的完整 C
if rank == 0:
    C_mpi = np.empty((N, N), dtype=np.float64)
else:
    C_mpi = None
comm.Gather(local_C, C_mpi, root=0)

if rank == 0:
    total_time = time.time() - t_start
    print(f"并行矩阵乘法完成.")
    print(f"  结果 C[0,0]     = {C_mpi[0,0]:.6f}")
    print(f"  结果 C[N/2,N/2] = {C_mpi[N//2,N//2]:.6f}")
    print(f"  结果 C[N-1,N-1] = {C_mpi[N-1,N-1]:.6f}")
    print(f"  Frobenius 范数   = {np.linalg.norm(C_mpi, 'fro'):.6f}")
    print(f"  总执行时间       = {total_time:.4f}s")
    print(f"  纯计算时间(rank0) = {local_comp_time:.4f}s")

# MPI_Barrier: 同步所有进程
comm.Barrier()
if rank == 0:
    print("阻塞通信版完成。")