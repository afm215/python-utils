import numpy as np

def generate_2D_rotation_matrix(theta:float, dtype=np.float32):
    """
    Generate a 2D rotational matrix
    INPUT:
    - theta: float, angle in degree
    Returns matrix of size (2,2)
    """
    theta_r = theta / 180 * np.pi
    return np.asarray([[np.cos(theta_r), - np.sin(theta_r)],
                        [np.sin(theta_r), np.cos(theta_r)]], dtype=dtype)