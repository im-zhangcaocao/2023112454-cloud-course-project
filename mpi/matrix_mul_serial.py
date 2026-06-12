import numpy as np
import time

N = 800

print("=" * 60)
print("串行矩阵乘法 (N={})".format(N))
print("=" * 60)

np.random.seed(42)
A = np.random.rand(N, N)
B = np.random.rand(N, N)

t0 = time.time()
C = A @ B
elapsed = time.time() - t0

print(f"矩阵维度: {N} x {N}")
print(f"执行时间: {elapsed:.4f} 秒")
print(f"结果矩阵 C[0,0] = {C[0,0]:.6f}")
print(f"结果矩阵 C[N/2,N/2] = {C[N//2,N//2]:.6f}")
print(f"结果矩阵 C[N-1,N-1] = {C[N-1,N-1]:.6f}")
print(f"Frobenius 范数: {np.linalg.norm(C, 'fro'):.6f}")
print("串行版完成。")