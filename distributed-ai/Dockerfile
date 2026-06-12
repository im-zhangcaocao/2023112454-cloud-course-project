FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /workspace

RUN pip install --no-cache-dir torchvision==0.16.0

COPY train_ddp.py /workspace/
COPY train_single.py /workspace/

ENTRYPOINT ["python"]