import numpy as np


def make_humanoid_wireframe():
    """
    This function creates a simple humanoid wireframe model.

    It returns:
    - vertices: an array of 3D points (N, 3)
    - edges: a list of index pairs defining the connections between vertices

    Local coordinates:
    x -> right
    y -> up
    z -> fake depth (used only for visual effect)
    """
    v = []

    # Head parameters
    head_y = 1.25          # vertical position of the head
    head_r = 0.20          # radius of the head
    head_n = 18            # number of points used to approximate the head circle

    # Create head as a circle of points
    for k in range(head_n):
        a = 2 * np.pi * k / head_n
        v.append([head_r * np.cos(a), head_y, head_r * np.sin(a)])

    # Center of the head
    head_center = len(v)
    v.append([0.0, head_y, 0.0])

    # Main body joints
    neck  = len(v); v.append([0.0, 1.05, 0.0])
    chest = len(v); v.append([0.0, 0.85, 0.0])
    hip   = len(v); v.append([0.0, 0.55, 0.0])

    # Shoulders
    shL = len(v); v.append([-0.35, 1.00, 0.0])
    shR = len(v); v.append([ 0.35, 1.00, 0.0])

    # Arms (elbow and hand)
    elL = len(v); v.append([-0.55, 0.80, 0.05])
    haL = len(v); v.append([-0.70, 0.62, 0.10])

    elR = len(v); v.append([ 0.55, 0.80, 0.05])
    haR = len(v); v.append([ 0.70, 0.62, 0.10])

    # Hips
    hipL = len(v); v.append([-0.20, 0.55, 0.0])
    hipR = len(v); v.append([ 0.20, 0.55, 0.0])

    # Legs (knee and foot)
    knL = len(v); v.append([-0.18, 0.30, 0.03])
    foL = len(v); v.append([-0.18, 0.05, 0.05])

    knR = len(v); v.append([ 0.18, 0.30, 0.03])
    foR = len(v); v.append([ 0.18, 0.05, 0.05])

    # Convert vertex list to numpy array
    vertices = np.array(v, dtype=np.float32)

    edges = []

    #Head edges: circular connections + links to head center
    for k in range(head_n):
        edges.append((k, (k + 1) % head_n))
        edges.append((k, head_center))

    # Body edges defining the humanoid skeleton
    edges += [
        (head_center, neck), (neck, chest), (chest, hip),
        (shL, shR), (shL, chest), (shR, chest),
        (shL, elL), (elL, haL),
        (shR, elR), (elR, haR),
        (hip, hipL), (hip, hipR),
        (hipL, knL), (knL, foL),
        (hipR, knR), (knR, foR),
    ]

    return vertices, edges
