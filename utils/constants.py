SAMPLE_INTERSECTIONS = [
    "Downtown", "Market Square", "University", "Hospital",
    "Shopping Mall", "Airport", "Central Park", "Stadium",
    "Residential A", "Residential B", "Industrial Zone"
]

SAMPLE_ROADS = [
    ("Downtown", "Market Square", 5),
    ("Downtown", "University", 8),
    ("Market Square", "Shopping Mall", 6),
    ("University", "Hospital", 4),
    ("Hospital", "Shopping Mall", 7),
    ("Shopping Mall", "Airport", 15),
    ("Downtown", "Central Park", 10),
    ("Central Park", "Stadium", 5),
    ("Stadium", "Airport", 8),
    ("University", "Residential A", 6),
    ("Residential A", "Residential B", 3),
    ("Residential B", "Industrial Zone", 9),
    ("Industrial Zone", "Airport", 7),
    ("Central Park", "Residential B", 12)
]

NODE_COORDS = {
    "Downtown": (40.7128, -74.0060),
    "Market Square": (40.7135, -74.0090),
    "University": (40.7150, -74.0030),
    "Hospital": (40.7170, -74.0045),
    "Shopping Mall": (40.7145, -74.0115),
    "Airport": (40.7200, -74.0200),
    "Central Park": (40.7180, -74.0070),
    "Stadium": (40.7195, -74.0130),
    "Residential A": (40.7165, -74.0005),
    "Residential B": (40.7190, -74.0010),
    "Industrial Zone": (40.7220, -74.0050)
}

TIME_WEIGHTS = {
    'morning': 1.5,
    'afternoon': 1.2,
    'evening': 1.8,
    'night': 0.9
}