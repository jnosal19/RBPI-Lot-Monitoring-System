# detector/roi_utils.py

def box_intersects_roi(box, roi, threshold=0.2):
    """
    Returns True if the intersection area between the vehicle box and ROI
    exceeds a given threshold of the vehicle's box area.
    """
    (x1, y1, x2, y2) = box
    (rx, ry, rw, rh) = roi

    roi_x2 = rx + rw
    roi_y2 = ry + rh

    # Intersection rectangle
    ix1 = max(x1, rx)
    iy1 = max(y1, ry)
    ix2 = min(x2, roi_x2)
    iy2 = min(y2, roi_y2)

    # If no overlap
    if ix2 <= ix1 or iy2 <= iy1:
        return False

    intersection_area = (ix2 - ix1) * (iy2 - iy1)
    box_area = (x2 - x1) * (y2 - y1)

    if box_area == 0:
        return False

    return (intersection_area / box_area) > threshold
