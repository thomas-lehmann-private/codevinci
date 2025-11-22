import cairosvg
import svgwrite

W, H = 1024, 768
M = W // 2

dwg = svgwrite.Drawing("docs/logo.svg", size=(W, H))

# ---------------------------
# Definitions: Clip-Regions (einmalig)
# ---------------------------
defs = dwg.defs
clip_left = dwg.clipPath(id="clip_left")
clip_left.add(dwg.rect(insert=(0, 0), size=(M, H)))
defs.add(clip_left)

clip_right = dwg.clipPath(id="clip_right")
clip_right.add(dwg.rect(insert=(M, 0), size=(M, H)))
defs.add(clip_right)

dwg.add(defs)

# ---------------------------
# Hintergrund
# ---------------------------
dwg.add(dwg.rect(insert=(0, 0), size=(M, H), fill="black"))
dwg.add(dwg.rect(insert=(M, 0), size=(M, H), fill="white"))

# ---------------------------
# Auge (aufgeteilt, nur durch expliziten Aufruf gezeichnet)
# ---------------------------
cx, cy = W / 2, H / 3
rx, ry = 250, 120  # Radien

def add_eye_half(side):
    """
    side: "left" oder "right"
    Linke Hälfte = weißes Auge / schwarze Iris
    Rechte Hälfte = schwarzes Auge / weiße Iris
    """
    if side == "left":
        clip_ref = "url(#clip_left)"
        sklera_color = "white"
        iris_color = "black"
        pupil_color = "white"  # kleine Pupille invertiert zur Iris
    elif side == "right":
        clip_ref = "url(#clip_right)"
        sklera_color = "black"
        iris_color = "white"
        pupil_color = "black"
    else:
        raise ValueError("side muss 'left' oder 'right' sein")

    # äußere Augenform (Sklera)
    dwg.add(dwg.ellipse(center=(cx, cy), r=(rx, ry),
                        fill=sklera_color, clip_path=clip_ref))

    # Iris
    dwg.add(dwg.ellipse(center=(cx, cy),
                        r=(rx * 0.4, ry * 0.4),
                        fill=iris_color, clip_path=clip_ref))

    # Pupille (kleiner Kreis in der Mitte, invertiert zur Iris)
    dwg.add(dwg.circle(center=(cx, cy), r=rx * 0.12,
                       fill=pupil_color, clip_path=clip_ref))

# explizit beide Hälften zeichnen
add_eye_half("left")
add_eye_half("right")

# ---------------------------
# Kästchen (3× Größe)
# ---------------------------
box_size = 180
y_box = cy + ry + 40

# Positionierung so dass Pfeil sauber dazwischen verläuft
left_box_x = M - (box_size * 1.6)
right_box_x = M + (box_size * 0.6)

dwg.add(dwg.rect((left_box_x, y_box), (box_size, box_size), fill="white"))
dwg.add(dwg.rect((right_box_x, y_box), (box_size, box_size), fill="black"))

# ---------------------------
# Pfeil von Kasten zu Kasten
# ---------------------------
arrow_y = y_box + box_size / 2
start_x = left_box_x + box_size  # rechter Rand des linken Kastens
end_x = right_box_x               # linker Rand des rechten Kastens

# Weißer Teil (links) - nur in linker Hälfte sichtbar
dwg.add(dwg.line(
    start=(start_x, arrow_y),
    end=(end_x, arrow_y),
    stroke="white",
    stroke_width=14,
    stroke_linecap="round",
    clip_path="url(#clip_left)"
))
dwg.add(dwg.polygon(
    points=[(end_x, arrow_y), (end_x - 44, arrow_y - 28), (end_x - 44, arrow_y + 28)],
    fill="white",
    clip_path="url(#clip_left)"
))

# Schwarzer Teil (rechts) - nur in rechter Hälfte sichtbar
dwg.add(dwg.line(
    start=(start_x, arrow_y),
    end=(end_x, arrow_y),
    stroke="black",
    stroke_width=14,
    stroke_linecap="round",
    clip_path="url(#clip_right)"
))
dwg.add(dwg.polygon(
    points=[(end_x, arrow_y), (end_x - 44, arrow_y - 28), (end_x - 44, arrow_y + 28)],
    fill="black",
    clip_path="url(#clip_right)"
))

# Optional: Boxes über dem Pfeil legen (damit Enden aussehen, als kämen sie aus den Boxen)
# aktuell sind die Boxen bereits gezeichnet und über dem Pfeil (weil Boxen vor Pfeil im Code),
# wenn du Pfeil unter/über den Boxen willst, passe die Reihenfolge an.

# ---------------------------
# Speichern
# ---------------------------
dwg.save()
print("logo_fixed.svg erzeugt!")

# convert
cairosvg.svg2png(url="docs/logo.svg", write_to="docs/logo.png")