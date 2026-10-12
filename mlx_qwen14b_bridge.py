import sys
from inversion_engine import InversionCoreEngine

def main():
    if len(sys.argv) > 1:
        inp = " ".join(sys.argv[1:])
        result = InversionCoreEngine.process_turn(decision=inp, round_num=1)
        print(result.get("reply", ""))
    else:
        print("Kullanım: python3 mlx_qwen14b_bridge.py '<analiz edilecek karar/ikilem>'")

if __name__ == "__main__":
    main()
