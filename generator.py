import collections
import copy
import heapq
import json
import random
import string
import sys

import solver

ASCII_MAX = 2**7
assert max(ord(c) for c in string.printable) < ASCII_MAX
CELL_MAX = 1e5


def find_path(begin, end, path_size, visited, neighbors, path, continuations):
  x, y = begin
  ex, ey = end
  if abs(x - ex) + abs(y - ey) > path_size:
    return None
  if begin == end and path_size == 0:
    return path + [begin]

  candidates = [(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]]
  new_neighbors = neighbors | set(candidates)
  random.shuffle(candidates)
  for x2, y2 in candidates:
    if (x2, y2) not in visited and (x2, y2) not in neighbors:
      continuations.append((
          (x2, y2),
          end,
          path_size - 1,
          visited | set([(x2, y2)]),
          new_neighbors,
          path + [begin]
      ))

  return None


def run_find(conts):
  if not conts:
    return None
  l = list(conts)
  random.shuffle(l)
  conts.clear()
  conts.extend(l)
  new_conts = collections.deque()
  while conts:
    c = conts.popleft()
    path = find_path(*c, new_conts)
    if path:
      return path
    if len(new_conts) > 100:
      path = run_find(new_conts)
      if path:
        return path
  path = run_find(new_conts)
  if path:
    return path
  return None


def fix_index(maze, expected, actual, bad_expected, bad_actual):
  ax, ay = bad_actual
  ex, ey = bad_expected

  delta = (maze[ey][ex] - maze[ay][ax]) // ASCII_MAX * ASCII_MAX
  delta = max(delta, ASCII_MAX)

  if maze[ay][ax] < CELL_MAX - delta:
    maze[ay][ax] += delta
  else:
    return

  if maze[ey][ex] > delta:
    maze[ey][ex] -= delta
  else:
    maze[ay][ax] -= delta


def score_path(path, maze):
  return sum(maze[p[1]][p[0]] for p in path)


def fix_maze(target, maze):
  target_set = frozenset(target)
  while True:
    path = solver.solve(maze, target[0], target[-1])
    if path == target:
      break
    path_set = frozenset(path)
    # print(
    #   len(target_set - path_set),
    #   len(path_set - target_set),
    #   score_path(target, maze),
    #   score_path(path, maze)
    # )
    bad_targets = [(p in path_set, -maze[p[1]][p[0]], p) for p in target_set]
    heapq.heapify(bad_targets)
    bad_paths = [(p in target_set, maze[p[1]][p[0]], p) for p in path_set]
    heapq.heapify(bad_paths)
    for i in range(max(
      1,
      len(target_set - path_set) // 10,
      len(path_set - target_set) // 10,
    )):
      _, w1, bad_target = heapq.heappop(bad_targets)
      _, w2, bad_path = heapq.heappop(bad_paths)
      # print(i, w1, w2)
      fix_index(maze, target, path, bad_target, bad_path)
  return maze


def random_offset():
  return ASCII_MAX * random.randrange(CELL_MAX // ASCII_MAX)


def random_char():
  return ord(random.choice(string.printable))


def create_path(path_size):
  path_manhattan = int(path_size ** 0.75)

  # Make sure a path of length == path_size exists between two points that are
  # path_manhattan distance apart.
  path_manhattan += (path_size - path_manhattan) % 2

  begin = (0, 0)
  end = random.choice(list(set(
    (begin[0] + dx, begin[1] + dy)
    for dx in range(-path_manhattan, path_manhattan + 1)
    for dy in (path_manhattan - dx, dx - path_manhattan)
    if dx**2 + dy**2 < path_manhattan ** 2 * .75
  )))

  conts = collections.deque([
      (
          begin,
          end,
          path_size,
          set(),
          set(),
          []
      )
  ])
  path = run_find(conts)
  min_x = min(x for x, y in path)
  min_y = min(y for x, y in path)
  max_x = max(x for x, y in path)
  max_y = max(y for x, y in path)
  width = max_x - min_x + 1
  height = max_y - min_y + 1
  return [
    (x - min_x + width // 10,
     y - min_y + height // 10)
    for x, y in path
  ]


def print_path(path, width, height):
  print('-'*(width+2))
  for y in range(height):
    print('|', end='')
    for x in range(width):
      print('#' if (x, y) in path else ' ', end='')
    print('|')
  print('-'*(width + 2))


def make_maze(path, width, height, message):
  path_set = frozenset(path)
  begin = path[0]
  end = path[-1]
  maze = [
    [
      0  # 'BEGIN'
      if (x, y) == begin
      else 0  # 'END'
      if (x, y) == end
      else ord(message[path.index((x, y)) - 1]) + random_offset()
      if (x, y) in path_set
      else random_char() + random_offset()
      for x in range(width)
    ] for y in range(height)
  ]
  maze = fix_maze(path, maze)
  maze[begin[1]][begin[0]] = 'BEGIN'
  maze[end[1]][end[0]] = 'END'
  return maze


def main():
  message = '''\
This string can be anything, and it will be encoded into a grid maze as the
shortest path from BEGIN to END in the maze. Sometimes the generator fails, but
80% of the time it works every time.'''

  assert sys.argv[1], 'Need cmdline argument to write file to'
  path_size = len(message) + 1

  path = create_path(path_size)
  height = max(p[1] for p in path) + min(p[1] for p in path)
  width = max(p[0] for p in path) + min(p[0] for p in path)

  print_path(path, width, height)
  maze = make_maze(path, width, height, message)

  with open(sys.argv[1], 'w') as f:
    json.dump({'maze': maze}, f)


if __name__ == '__main__':
  main()
