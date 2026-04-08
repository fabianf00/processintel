def isProcessTreeEqual(tree1, tree2):
    """Recursively compares two trees for structural equivalence.

    Parameters
    ----------
    tree1 : str | int | tuple
        First process tree.
    tree2 : str | int | tuple
        Second process tree.

    Returns
    -------
    bool
        True if the trees are structurally equivalent, Fals otherwise.

    Raises
    ------
    Exception
        Invalid tree type.
    """
    if type(tree1) != type(tree2):
        return False

    if isinstance(tree1, str) or isinstance(tree1, int):
        return tree1 == tree2

    if not isinstance(tree1, tuple):
        raise Exception("Invalid tree type")

    if len(tree1) != len(tree2):
        return False

    operation = tree1[0]
    if operation != tree2[0]:
        return False

    # ordered cuts first
    if operation == "seq":
        return all(isProcessTreeEqual(tree1[i], tree2[i]) for i in range(1, len(tree1)))
    if operation == "loop":
        if not isProcessTreeEqual(tree1[1], tree2[1]):
            return False

    for i in range(1, len(tree1)):
        foundEqual = False
        for j in range(1, len(tree2)):
            if isProcessTreeEqual(tree1[i], tree2[j]):
                foundEqual = True
                break
        if not foundEqual:
            return False

    return True
