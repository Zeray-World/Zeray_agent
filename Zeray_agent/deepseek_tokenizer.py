from pathlib import Path
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_file(str(Path(__file__).parent / "tokenizer.json"))

def token_compute(input_token_text):
    _ = len(tokenizer.encode(input_token_text).ids)
    return _

if __name__ == '__main__':

    result = 1
    while result !='0':
        result = input("input(0退出):")
        ids = tokenizer.encode(result).ids
        print("ID:", ids)
        print("花费token:", len(ids))

        prices = input("价格_每百万token(命中缓存 未命中缓存 输出):").split()
        cache_hit, cache_miss, output = float(prices[0]), float(prices[1]), float(prices[2])

        print("命中缓存费用:", f"{(len(ids) / 1000000) * cache_hit:.8f}")
        print("未命中缓存费用:", f"{(len(ids) / 1000000) * cache_miss:.8f}")
        print("输出费用:", f"{(len(ids) / 1000000) * output:.8f}\n")
