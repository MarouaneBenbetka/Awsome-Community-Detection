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


def save_predicted_labels(labels, file_path):

    if not file_path.endswith('.txt'):
        file_path = file_path+'.txt'

    with open(file_path, 'w') as file:
        for node, label in labels:
            file.write(f"{node} {label}\n")
    print(f"Predicted labels saved to {file_path}")
