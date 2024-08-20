import nest_asyncio
import asyncio
import tempfile
import os
import threading
from playwright.async_api import async_playwright

# Apply nest_asyncio to handle the running event loop
nest_asyncio.apply()

async def html_file_to_pdf(html_file_path: str, output_path: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Read HTML content from the local file
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Set the HTML content
        await page.set_content(html_content, wait_until='networkidle')

        # Generate PDF with options
        await page.pdf(
            path=output_path,
            format='A4',  # Set the paper format
            print_background=True,  # Print background graphics
            margin={
                'top': '20px',
                'right': '20px',
                'bottom': '20px',
                'left': '20px'
            }
        )
        
        await browser.close()

def delete_file_after_delay(file_path: str, delay: int):
    """ Delete the file after a specified delay (in seconds). """
    def delete():
        import time
        time.sleep(delay)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} has been deleted after {delay} seconds.")
        else:
            print(f"File {file_path} not found for deletion.")
    
    thread = threading.Thread(target=delete)
    thread.start()

# Local path to the HTML file
html_file_path = 'pdf_single.html'  # Change this to your actual file path

# Extract the filename without extension and use it for the PDF
file_base_name = os.path.splitext(os.path.basename(html_file_path))[0]
output_pdf_path = os.path.join(tempfile.gettempdir(), f'{file_base_name}.pdf')

# Run the asynchronous function to convert HTML to PDF
asyncio.get_event_loop().run_until_complete(html_file_to_pdf(html_file_path, output_pdf_path))

# Provide a link to download the PDF (Manual download needed)
print(f"PDF has been generated and saved to: {output_pdf_path}")

# Set the file to be deleted after 30 minutes (1800 seconds)
delete_file_after_delay(output_pdf_path, 5)