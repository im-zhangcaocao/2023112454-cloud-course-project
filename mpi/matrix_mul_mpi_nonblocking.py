from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

N = 800

if rank == 0:
    print("=" * 60)
    print("MPI 并行矩阵乘法 - 非阻塞通信版 (N={}, P={})".format(N, size))
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

# 使用非阻塞 Scatter: comm.Iscatter 立即返回请求对象
# 数据流向: root=0 持有完整 A → 各进程异步接收 rows_per_proc 行
req_scatter = comm.Iscatter(A, local_A, root=0)

# 使用非阻塞 Bcast: comm.Ibcast 立即返回请求对象
# 数据流向: root=0 → 各进程异步接收完整 B
req_bcast = comm.Ibcast(B, root=0)

# 等待通信完成，同时可在此间隙进行其他计算（此处为简单示例）
MPI.Request.Waitall([req_scatter, req_bcast])

t_comp_start = time.time()
local_C = local_A @ B
t_comp_end = time.time()
local_comp_time = t_comp_end - t_comp_start

# 非阻塞 Gather: comm.Igather 立即返回
# 数据流向: 各进程 local_C → root=0 异步接收
if rank == 0:
    C_mpi_nb = np.empty((N, N), dtype=np.float64)
else:
    C_mpi_nb = None
req_gather = comm.Igather(local_C, C_mpi_nb, root=0)

# MPI_Wait: 等待非阻塞 Gather 完成
req_gather.Wait()

if rank == 0:
    total_time = time.time() - t_start
    print(f"非阻塞并行矩阵乘法完成.")
    print(f"  结果 C[0,0]     = {C_mpi_nb[0,0]:.6f}")
    print(f"  结果 C[N/2,N/2] = {C_mpi_nb[N//2,N//2]:.6f}")
    print(f"  结果 C[N-1,N-1] = {C_mpi_nb[N-1,N-1]:.6f}")
    print(f"  Frobenius 范数   = {np.linalg.norm(C_mpi_nb, 'fro'):.6f}")
    print(f"  总执行时间       = {total_time:.4f}s")
    print(f"  纯计算时间(rank0) = {local_comp_time:.4f}s")

comm.Barrier()
if rank == 0:
    print("非阻塞通信版完成。")