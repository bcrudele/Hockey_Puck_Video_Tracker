from trackHSV import trackHSV
if __name__ == "__main__":
    tracker = trackHSV(1, (5, 150, 150), (15, 255, 255))
    tracker.run()
