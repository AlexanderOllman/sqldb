import fitz  # PyMuPDF

def modify_customer_name(pdf_path, new_name, opp_id, ucid, output_path):
    # Open the PDF file
    document = fitz.open(pdf_path)
    
    # Iterate through the pages
    for page_num in range(len(document)):
        page = document[page_num]
        text_instances = page.search_for("Customer Name: Not Available")
        num_instances = page.search_for("5138883180-01")
        
        # If "Customer Name: Not Available" is found, replace it
        for inst in text_instances:
            # Define the white background rectangle
            rect = fitz.Rect(inst.x0-10, inst.y0, inst.x1, inst.y1+20)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
            
            # Insert new text with matching font
                        # Insert new text slightly to the right and down
            x_offset = 13.5  # Adjust this value as needed
            y_offset = 6  # Adjust this value as needed
            page.insert_text((inst.x0 + x_offset, inst.y0 + y_offset), f"Customer Name: {new_name}", fontsize=8, color=(0, 0, 0))

            x_offset2 = 13.5  # Adjust this value as needed
            y_offset2 = 24  # Adjust this value as needed
            page.insert_text((inst.x0 + x_offset2, inst.y0 + y_offset2), f"Opportunity ID: {opp_id}", fontsize=8, color=(0, 0, 0))

        for inst in num_instances:
            if inst == num_instances[0]:
                # Define the white background rectangle
                rect = fitz.Rect(inst.x0-10, inst.y0, inst.x1, inst.y1)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # Insert new text with matching font
                            # Insert new text slightly to the right and down
                x_offset = 0  # Adjust this value as needed
                y_offset = 7.5  # Adjust this value as needed
                page.insert_text((inst.x0 - x_offset, inst.y0 + y_offset), f"{ucid}", fontsize=9.8, color=(0, 0, 0))

            if inst == num_instances[1]:
                # Define the white background rectangle
                rect = fitz.Rect(inst.x0-10, inst.y0, inst.x1, inst.y1)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                
                # Insert new text with matching font
                            # Insert new text slightly to the right and down
                x_offset = 0  # Adjust this value as needed
                y_offset = 7.5  # Adjust this value as needed
                page.insert_text((inst.x0 - x_offset, inst.y0 + y_offset), f"{ucid}", fontsize=8.8, color=(0, 0, 0))


    # Save the modified PDF to a new file
    document.save(output_path)

# Example usage
pdf_path = "quote_template.pdf"
new_name = "John Doe"
opp_id = "OPP-87299489"
ucid = "5188494180-01"
output_path = "quote.pdf"

modify_customer_name(pdf_path, new_name, opp_id, ucid, output_path)
