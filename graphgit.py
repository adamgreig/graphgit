import git
import pygraphviz
import sys
import hashlib
import os.path

G = pygraphviz.AGraph(strict=False, directed=True)
G.graph_attr['rankdir'] = 'RL'
G.graph_attr['overlap'] = 'false'
G.node_attr['colorscheme'] = 'set19'
G.edge_attr['colorscheme'] = 'set19'
G.edge_attr['dir'] = 'back'

commits = {}
names = set()

def name_to_int(name):
    return (int(hashlib.md5(name).hexdigest(), 16) % 9) + 1

def process_commit(c):
    global G
    while not G.has_node(c.hexsha[0:5]):
        names.add(c.author.name)
        G.add_node(c.hexsha[0:5], color=name_to_int(c.author.name))
        commits[c.hexsha[0:5]] = c
        for p in c.parents:
            process_commit(p)
            G.add_edge(c.hexsha[0:5], p.hexsha[0:5],
                    color=name_to_int(c.author.name))

def main():
    global G

    if len(sys.argv) == 1:
        print "Usage: {0} <path to git repo>".format(sys.argv[0])
        sys.exit(0)

    path = sys.argv[1]

    if path[-1] == '/':
        path = path[:-1]

    title = os.path.basename(path)
    G.graph_attr['label'] = title

    try:    
        repo = git.Repo(path)
    except git.exc.NoSuchPathError:
        print "Error: invalid repository path."
        sys.exit(0)

    for head in repo.heads + sum([remote.refs for remote in repo.remotes], []):
        process_commit(head.commit)
        G.add_node(head.name, shape='box',
                color=name_to_int(head.commit.author.name))
        G.add_edge(head.name, head.commit.hexsha[0:5], dir='none')

    for name in names:
        G.add_node(name, color=name_to_int(name))

    with open(title + ".dot", "w") as f:
        f.write(str(G))

    G.layout()
    G.draw(title + ".png")

if __name__ == "__main__":
    main()
