def read_community_labels_file_reel(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        res = []
        for node, label in enumerate(lines):
            res.append((int(node), int(label)+1))
        return res


def read_community_labels_file_synth(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        res = []
        for line in lines:
            node, label = line.split()
            res.append((int(node)-1, int(label)))
        return res
