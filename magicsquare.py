"""幻方（Magic Square）生成器与验证器。

奇数阶幻方用暹罗法（Siamese method）构造；
偶数阶（4 的倍数）用对角线交换法构造；
4k+2 阶暂不支持（LUX 方法不在小巧范围内）。

纯标准库：argparse、sys。
"""

import argparse
import sys


def magic_constant(n):
    """幻和公式：n(n^2+1)/2。"""
    return n * (n * n + 1) // 2


def siamese(n):
    """暹罗法构造奇数阶幻方。n 必须为奇数。"""
    if n % 2 == 0:
        raise ValueError("暹罗法只支持奇数阶")
    grid = [[0] * n for _ in range(n)]
    r, c = 0, n // 2
    for k in range(1, n * n + 1):
        grid[r][c] = k
        nr, nc = (r - 1) % n, (c + 1) % n
        if grid[nr][nc] != 0:  # 被占，改走正下方
            nr, nc = (r + 1) % n, c
        r, c = nr, nc
    return grid


def doubly_even(n):
    """对角线交换法构造 4k 阶幻方。"""
    if n % 4 != 0:
        raise ValueError("对角线交换法只支持 4 的倍数阶")
    grid = [[r * n + c + 1 for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            on_diag = (r % 4 == c % 4) or (r % 4 + c % 4 == 3)
            if on_diag:
                grid[r][c] = n * n + 1 - grid[r][c]
    return grid


def generate(n):
    """按阶数自动选方法构造幻方；4k+2 阶抛错。"""
    if n < 3:
        raise ValueError("阶数至少为 3")
    if n % 2 == 1:
        return siamese(n)
    if n % 4 == 0:
        return doubly_even(n)
    raise ValueError(f"不支持 {n} 阶（4k+2 阶不在小巧范围内）")


def check(grid):
    """验证是否为标准幻方（1..n^2 各用一次，行列对角和相等）。
    返回 (ok, reason)。"""
    n = len(grid)
    if n == 0 or any(len(row) != n for row in grid):
        return False, "不是方阵"
    flat = sorted(v for row in grid for v in row)
    if flat != list(range(1, n * n + 1)):
        return False, "数字不是 1..n^2 的排列"
    target = magic_constant(n)
    for i, row in enumerate(grid):
        if sum(row) != target:
            return False, f"第 {i + 1} 行和 {sum(row)} != 幻和 {target}"
    for c in range(n):
        s = sum(grid[r][c] for r in range(n))
        if s != target:
            return False, f"第 {c + 1} 列和 {s} != 幻和 {target}"
    d1 = sum(grid[i][i] for i in range(n))
    d2 = sum(grid[i][n - 1 - i] for i in range(n))
    if d1 != target or d2 != target:
        return False, f"对角线和 {d1}/{d2} != 幻和 {target}"
    return True, f"标准幻方，幻和 {target}"


def parse_square(text):
    """从文本解析方阵，行以换行分隔，数字以空格/逗号分隔。"""
    rows = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        rows.append([int(x) for x in ln.replace(",", " ").split()])
    return rows


def render(grid):
    n = len(grid)
    w = len(str(n * n))
    return "\n".join(" ".join(f"{v:>{w}}" for v in row) for row in grid)


def main(argv=None):
    p = argparse.ArgumentParser(prog="magicsquare", description="幻方生成器与验证器")
    p.add_argument("--n", type=int, default=3, help="阶数（默认 3；支持奇数阶和 4k 阶）")
    p.add_argument("--check", metavar="FILE", nargs="?", const="-",
                   help="验证方阵（文件路径或 - 从 stdin 读）")
    args = p.parse_args(argv)

    if args.check is not None:
        try:
            text = sys.stdin.read() if args.check == "-" else open(args.check, encoding="utf-8").read()
            grid = parse_square(text)
        except (OSError, ValueError) as e:
            print(f"读取失败：{e}", file=sys.stderr)
            return 2
        ok, reason = check(grid)
        print(f"{'✅' if ok else '❌'} {reason}")
        print(render(grid))
        return 0 if ok else 1

    try:
        grid = generate(args.n)
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 2
    print(f"幻方 {args.n}×{args.n}，幻和 = {magic_constant(args.n)}：\n")
    print(render(grid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
