

def read_community_labels_file_reel(file_path):
    """
    Reads the ground truth files for the reel datasets.

    Args:
        file_path (str): The path to the file containing the community labels.

    Returns:
        list: A list of tuples representing the node and its corresponding label.
              Each tuple contains the node index (int) and the label (int+1).
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
        res = []
        for node, label in enumerate(lines):
            res.append((int(node), int(label)+1))
        return res


def read_community_labels_file_synth(file_path):
    """
    Reads the community.dat files for synthetic datasets.

    Args:
        file_path (str): The path to the community.dat file.

    Returns:
        list: A list of tuples containing the node and its corresponding label.
              Each tuple is in the format (node, label), where node is an integer
              representing the node index (starting from 0) and label is an integer
              representing the community label.
    """

    res = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        res = []
        for line in lines:
            node, label = line.split()
            res.append((int(node)-1, int(label)))

    return res


def save_predicted_labels(labels, file_path):
    """
    Save the predicted values of communities for each node in a txt file.

    Args:
        labels (list): A list of tuples containing the node and its corresponding label.
        file_path (str): The path of the file to save the predicted labels.

    Returns:
        None
    """
    if not file_path.endswith('.txt'):
        file_path = file_path+'.txt'

    with open(file_path, 'w') as file:
        for node, label in labels:
            file.write(f"{node} {label}\n")
    print(f"Predicted labels saved to {file_path}")
