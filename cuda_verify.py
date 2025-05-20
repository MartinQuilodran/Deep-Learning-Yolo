import torch

print("¿CUDA disponible?:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Nombre de GPU:", torch.cuda.get_device_name(0))
    print("Número de GPUs:", torch.cuda.device_count())
else:
    print("⚠️ Aún no se está usando la GPU.")
