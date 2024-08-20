from flask import Flask, request, jsonify, send_file
import tempfile
import os
from werkzeug.utils import secure_filename
from playwright.async_api import async_playwright
import asyncio
import threading
import time

app = Flask(__name__)

class HtmlToPdfConverter:
    def __init__(self, html_file_path: str, delete_delay: int):
        self.html_file_path = html_file_path
        self.delete_delay = delete_delay
        self.output_pdf_path = None

        # Apply nest_asyncio to handle the running event loop
        import nest_asyncio
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
            self.output_pdf_path = os.path.join('/tmp', f'{os.path.splitext(os.path.basename(self.html_file_path))[0]}.pdf')
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
            if os.path.exists(self.html_file_path):
                os.remove(self.html_file_path)
                print(f"Temporary file {self.html_file_path} has been deleted after {self.delete_delay} seconds.")
            else:
                print(f"Temporary file {self.html_file_path} not found for deletion.")
        
        thread = threading.Thread(target=delete)
        thread.start()

    def convert(self):
        # Run the asynchronous function to convert HTML to PDF
        asyncio.get_event_loop().run_until_complete(self.html_file_to_pdf())

        # Set the file to be deleted after the specified delay
        self.delete_file_after_delay()
        return self.output_pdf_path

@app.route('/convert', methods=['POST'])
def convert_html_to_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the uploaded file to a temporary location
    temp_html_file_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
    file.save(temp_html_file_path)

    # Create a converter instance
    converter = HtmlToPdfConverter(temp_html_file_path, 1800)
    pdf_path = converter.convert()

    # Delete the temporary HTML file after conversion is complete
    if os.path.exists(temp_html_file_path):
        os.remove(temp_html_file_path)

    # Return the PDF file to the user
    return send_file(pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path))# attachment_filename=os.path.basename(pdf_path))

if __name__ == '__main__':
    app.run(debug=True)
