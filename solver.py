import heapq
import json
import sys


def parse_maze(raw_maze):
  begin, end = [None], [None]

  def convert_cell(x, y, cell):
    try:
      return int(cell)
    except ValueError:
      if cell == 'BEGIN':
        begin[0] = (x, y)
      elif cell == 'END':
        end[0] = (x, y)
      else:
        raise
      return 0

  return [
    [convert_cell(x, y, cell) for x, cell in enumerate(row)]
    for y, row in enumerate(raw_maze)
  ], begin[0], end[0]


def solve(maze, begin, end):
  heap = [(0, begin, None)]
  prev = {}
  while heap:
    dist, pos, prev_pos = heapq.heappop(heap)
    if pos in prev:
      continue
    prev[pos] = prev_pos
    if pos == end:
      break
    x, y = pos
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
      x2 = x + dx
      y2 = y + dy
      if 0 <= x2 < len(maze[0]) and 0 <= y2 < len(maze):
        heapq.heappush(heap, (dist + maze[y2][x2], (x2, y2), pos))
  else:
    raise RuntimeError("couldn't find end")

  path = [end]
  while prev[path[-1]] is not None:
    path.append(prev[path[-1]])

  return list(reversed(path))


def main():
  with open(sys.argv[1]) as f:
    raw_maze = json.load(f)

  maze, begin, end = parse_maze(raw_maze['maze'])
  solution = solve(maze, begin, end)
  letters = solution[1:-1]
  print(''.join(chr(maze[y][x] % 2**7) for x, y in letters))


if __name__ == '__main__':
  main()
