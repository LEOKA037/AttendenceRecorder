from PIL import Image, ImageDraw, ImageFont
import os

def generate_attendance_image(header, data_rows, color_mapping, filename="attendance.png", logo_path=None):
    # Image settings
    font_path = "arial.ttf" # Default system font
    try:
        font = ImageFont.truetype(font_path, 18)
        bold_font = ImageFont.truetype(font_path, 24)
    except IOError:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()

    cell_padding = 10
    row_height = 40
    header_height = 50
    circle_radius = 10
    logo_height = 60
    top_padding = 10

    # Calculate column widths
    column_widths = [0] * len(header)
    # First column (Team Member) width
    team_member_col_width = 0
    for row in data_rows:
        team_member_col_width = max(team_member_col_width, font.getbbox(str(row[0]))[2])
    column_widths[0] = team_member_col_width + cell_padding * 2

    # Other columns (dates) width
    for i in range(1, len(header)):
        column_widths[i] = bold_font.getbbox(header[i])[2] + cell_padding * 2
    
    # Image dimensions
    total_width = sum(column_widths)
    table_height = header_height + len(data_rows) * row_height
    total_height = table_height + logo_height + top_padding

    img = Image.new('RGB', (total_width, total_height), color = (255, 255, 255))
    d = ImageDraw.Draw(img)

    # Draw logo and title
    if logo_path:
        try:
            logo = Image.open(logo_path)
            ratio = logo_height / logo.height
            logo_width = int(logo.width * ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            img.paste(logo, (cell_padding, top_padding))
            title_x_offset = cell_padding + logo_width + cell_padding
        except FileNotFoundError:
            title_x_offset = cell_padding
    else:
        title_x_offset = cell_padding

    d.text((title_x_offset, top_padding + (logo_height - bold_font.getbbox("Attendance Report")[3]) / 2), 
           "Attendance Report", fill=(0, 0, 0), font=bold_font)

    # Draw header
    y_offset = logo_height + top_padding
    x_offset = 0
    for i, col_name in enumerate(header):
        d.rectangle([x_offset, y_offset, x_offset + column_widths[i], y_offset + header_height], fill=(200, 200, 200), outline=(0, 0, 0))
        d.text((x_offset + cell_padding, y_offset + (header_height - bold_font.getbbox(col_name)[3]) / 2), col_name, fill=(0, 0, 0), font=bold_font)
        x_offset += column_widths[i]

    # Draw rows
    y_offset += header_height
    for row_idx, row_data in enumerate(data_rows):
        x_offset = 0
        fill_color = (240, 240, 240) if row_idx % 2 == 0 else (255, 255, 255)
        for i, cell_data in enumerate(row_data):
            d.rectangle([x_offset, y_offset, x_offset + column_widths[i], y_offset + row_height], fill=fill_color, outline=(0, 0, 0))
            if i == 0: # Team member name
                d.text((x_offset + cell_padding, y_offset + (row_height - font.getbbox(str(cell_data))[3]) / 2), str(cell_data), fill=(0, 0, 0), font=font)
            else: # Status icon
                color = color_mapping.get(cell_data, "#000000") # Default to black if status not in map
                center_x = x_offset + column_widths[i] / 2
                center_y = y_offset + row_height / 2
                bounding_box = [
                    (center_x - circle_radius, center_y - circle_radius),
                    (center_x + circle_radius, center_y + circle_radius)
                ]
                d.ellipse(bounding_box, fill=color, outline="black")
            x_offset += column_widths[i]
        y_offset += row_height
    
    # Ensure the output directory exists
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    img.save(output_path)
    return output_path

