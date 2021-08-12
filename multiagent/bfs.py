from collections import deque


def testLegal(maze, p):
    if isinstance(maze, list):
        height = len(maze)
        width = len(maze[0])
    else:
        height = maze.height
        width = maze.width

    if p[0] < 0 or p[0] > width:
        return False
    if p[1] < 0 or p[1] > height:
        return False
    if maze[p[0]][p[1]] == True:
        return False

    return True


def make_graph(maze):
    graph = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    height = maze.height
    width = maze.width

    for x in range(width):
        for y in range(height):
            p = (x, y)
            node = {'point': p, 'neighbors': []}
            if testLegal(maze, p):
                for d in directions:
                    neighbor = (p[0] + d[0], p[1] + d[1])
                    if testLegal(maze, neighbor):
                        node['neighbors'].append(neighbor)
            graph.append(node)
    return graph


def bfs(start, goal, graph):
    """
    finds a shortest path in undirected `graph` between `start` and `goal`. 
    If no path is found, returns `None`
    """
    if start == goal:
        return [start]
    visited = {start}
    queue = deque([(start, [])])

    while queue:
        current, path = queue.popleft()
        visited.add(current)

        neighbors = None
        for node in graph:
            if node['point'] == current:
                neighbors = node['neighbors']

        if neighbors != None:
            for neighbor in neighbors:
                if neighbor == goal:
                    return path + [current, neighbor]
                if neighbor in visited:
                    continue
                queue.append((neighbor, path + [current]))
                visited.add(neighbor)
    return []  # no path found. not strictly needed


def search(begin, end, maze):
    graph = make_graph(maze)
    return bfs(begin, end, graph)
