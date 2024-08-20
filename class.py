import nest_asyncio
import asyncio
import tempfile
import os
import threading
from playwright.async_api import async_playwright

class HtmlToPdfConverter:
    def __init__(self, html_file_path: str, delete_delay: int):
        self.html_file_path = html_file_path
        self.delete_delay = delete_delay
        self.output_pdf_path = None

        # Apply nest_asyncio to handle the running event loop
        nest_asyncio.apply()

    async def html_file_to_pdf(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Read HTML content from the local file
            with open(self.html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # Set the HTML content
            await page.set_content(html_content, wait_until='networkidle')

            # Generate PDF with options
            await page.pdf(
                path=self.output_pdf_path,
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

    def delete_file_after_delay(self):
        """Delete the file after a specified delay (in seconds)."""
        def delete():
            import time
            time.sleep(self.delete_delay)
            if os.path.exists(self.output_pdf_path):
                os.remove(self.output_pdf_path)
                print(f"File {self.output_pdf_path} has been deleted after {self.delete_delay} seconds.")
            else:
                print(f"File {self.output_pdf_path} not found for deletion.")
        
        thread = threading.Thread(target=delete)
        thread.start()

    def convert(self):
        # Extract the filename without extension and use it for the PDF
        file_base_name = os.path.splitext(os.path.basename(self.html_file_path))[0]
        self.output_pdf_path = os.path.join(tempfile.gettempdir(), f'{file_base_name}.pdf')

        # Run the asynchronous function to convert HTML to PDF
        asyncio.get_event_loop().run_until_complete(self.html_file_to_pdf())

        # Provide a link to download the PDF (Manual download needed)
        print(f"PDF has been generated and saved to: {self.output_pdf_path}")

        # Set the file to be deleted after the specified delay
        self.delete_file_after_delay()
        return self.output_pdf_path

# Example usage:
html_file_path = 'pdf_single.html'  # Change this to your actual file path

converter = HtmlToPdfConverter(html_file_path, 1000)
pa =  converter.convert()
print(f'find {pa}')