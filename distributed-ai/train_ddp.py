import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
from torchvision import datasets, transforms
import time

BATCH_SIZE = 64
EPOCHS = 5
LEARNING_RATE = 0.001


class MNISTCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = nn.functional.relu(x)
        x = self.conv2(x)
        x = nn.functional.relu(x)
        x = nn.functional.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = nn.functional.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return nn.functional.log_softmax(x, dim=1)


def setup_ddp():
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    world_size = int(os.environ.get("WORLD_SIZE", 1))
    rank = int(os.environ.get("RANK", 0))

    dist.init_process_group(backend="gloo")
    torch.manual_seed(42)

    return local_rank, world_size, rank


def cleanup():
    dist.destroy_process_group()


def train_ddp():
    local_rank, world_size, rank = setup_ddp()
    device = torch.device("cpu")

    if rank == 0:
        print("=" * 60)
        print(f"PyTorch DDP 分布式训练 MNIST CNN (World Size={world_size})")
        print("=" * 60)
        print(f"全局 Rank: {rank}, 本地 Rank: {local_rank}, 总进程数: {world_size}")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST(
        "./data", train=True, download=True, transform=transform
    )
    test_dataset = datasets.MNIST(
        "./data", train=False, download=True, transform=transform
    )

    train_sampler = DistributedSampler(
        train_dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=True
    )
    test_sampler = DistributedSampler(
        test_dataset,
        num_replicas=world_size,
        rank=rank,
        shuffle=False
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        sampler=train_sampler,
        num_workers=2
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        sampler=test_sampler,
        num_workers=2
    )

    model = MNISTCNN().to(device)

    # 使用 DDP 包装模型，启用梯度同步
    # DDP 在 backward() 时自动触发 AllReduce 梯度同步
    model = DDP(model)

    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.functional.nll_loss

    total_time = 0
    for epoch in range(1, EPOCHS + 1):
        train_sampler.set_epoch(epoch)
        model.train()

        t0 = time.time()
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            # backward() 内部自动执行 AllReduce:
            # 各进程计算本地梯度 → AllReduce 求平均 → 所有进程获得一致的全局梯度
            loss.backward()
            optimizer.step()

        epoch_time = time.time() - t0
        total_time += epoch_time

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += len(data)

        accuracy = 100.0 * correct / total if total > 0 else 0
        if rank == 0:
            print(f"Epoch {epoch}: Loss={loss.item():.4f}, Accuracy={accuracy:.2f}%, Time={epoch_time:.2f}s")

    if rank == 0:
        print(f"\n总计训练时间: {total_time:.2f}s")
        print(f"平均每 epoch 时间: {total_time/EPOCHS:.2f}s")
        print(f"最终准确率: {accuracy:.2f}%")

        torch.save(model.module.state_dict(), "mnist_cnn_ddp.pth")
        print("模型已保存至 mnist_cnn_ddp.pth")

    cleanup()


if __name__ == "__main__":
    train_ddp()