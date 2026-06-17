def centroid(bolts):
    x = sum(b.x for b in bolts) / len(bolts)
    y = sum(b.y for b in bolts) / len(bolts)
    return x, y
