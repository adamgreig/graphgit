import git
import pygraphviz
import sys

G = pygraphviz.AGraph(strict=False, directed=True)
G.edge_attr['dir'] = 'back'

commits = {}

def process_commit(c):
    global G
    while not G.has_node(c.hexsha[0:5]):
        G.add_node(c.hexsha[0:5])
        commits[c.hexsha[0:5]] = c
        for p in c.parents:
            process_commit(p)
            G.add_edge(c.hexsha[0:5], p.hexsha[0:5])

def main():
    global G

    if len(sys.argv) == 1:
        print "Usage: {0} <path to git repo>".format(sys.argv[0])
        sys.exit(0)
    try:    
        repo = git.Repo(sys.argv[1])
    except git.exc.NoSuchPathError:
        print "Error: invalid repository path."
        sys.exit(0)

    for head in repo.heads:
        process_commit(head.commit)

    print G

if __name__ == "__main__":
    main()
