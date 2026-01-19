import torch
import numpy
try:
    print(f"NumPy Version: {numpy.__version__}")
    print(f"Torch Version: {torch.__version__}")
    print(f"XPU exists in torch: {hasattr(torch, 'xpu')}")
    print(f"XPU is available: {torch.xpu.is_available() if hasattr(torch, 'xpu') else 'N/A'}")
    print("✅ System stable for 2017 Mac!")
except Exception as e:
    print(f"❌ Error: {e}")