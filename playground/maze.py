

def getNumMinJumps(maze, k):
    big_num = 1e15
    def pretty_print_maze(maze):
        for row in maze:
            print(row)
    pretty_print_maze(maze)
    if maze[-1][-1] == 1:
        # There is an osbstacle at the desired position
        return -1
    n, m = len(maze), len(maze[0])
    
    if n == 1 and m == 1:
        # We already are at the target position
        return 0
    
    directions = {"Up": [-1, 0], "Down": [1, 0], "Right": [0, 1], "Left": [0, -1]}
    visited = set()
    def dfs(i, j, cache={}):
        

        if i < 0 or j < 0 or i >= n or j >=m or maze[i][j] == 1:
            # if at obstacle or exceeding bounds
            return set(), -1
        
        if i == n -1 and j == m - 1:
            # if reach target
            return set(["Up", "Down", "Right", "Left"]), 0

        cache_key = str(i) + "-" + str(j)
        if cache_key in visited:
            return set(), -1
        
        if cache_key in cache:
            return cache[cache_key]
        
        best_count = big_num
        good_directions = set()
        visited.add(cache_key)
        for dir_name, dire in directions.items():
            for z in range(1, k + 1):
                new_i, new_j = i + z * dire[0], j + z * dire[1]
                dir_set, curr_count = dfs(new_i, new_j, cache)
                if curr_count < 0: # done with this direction
                    break
                curr_count = curr_count if dir_name in dir_set else curr_count + 1
                if curr_count < best_count:
                    good_directions.clear()
                    good_directions.add(dir_name)
                    best_count = curr_count
                elif curr_count == best_count:
                    good_directions.add(dir_name)
        
        visited.remove(cache_key)
        best_count = -2 if best_count == big_num else best_count
        cache[cache_key] = [good_directions, best_count]
        return [good_directions, best_count]

    return 1 + dfs(0, 0)[-1]


if __name__ == "__main__":
    test_cases = [
        [[[0, 0, 0],
          [1, 1, 0]], 1],

        [[[0, 0, 0],
          [1, 0, 0],
          [1, 0, 1],
          [0, 0, 1],
          [1, 0, 0], 
          [0, 0, 1],
          [0, 1, 1],
          [0, 0, 0],
          [1, 1, 0]], 5],

        [[[0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [1, 1, 1, 1, 1, 1, 1, 0]], 10],
        
        [[[0, 0, 0, 0, 0],
          [1, 1, 1, 1, 0],
          [1, 0, 0, 0, 0],
          [1, 0, 1, 1, 1], 
          [0, 0, 0, 0, 1],
          [0, 1, 1, 1, 1],
          [0, 1, 0, 0, 0],
          [0, 0, 0, 1, 0],
          [1, 1, 1, 1, 0]], 1]
    ]
    for tc in test_cases:
        result = getNumMinJumps(*tc)
        print(f"Result: {result}")
