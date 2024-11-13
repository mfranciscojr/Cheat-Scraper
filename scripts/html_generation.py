# scripts/html_generation.py

import os
import logging
import webbrowser
from scripts.utils import sanitize_filename
from urllib.parse import quote
from colorama import Fore

def generate_html_per_game(game_data):
    # (Include the full function code from your original script)
    # This function generates the HTML file for a specific game.
    # For brevity, you can keep the function as is, or split further if needed.
    # The full code is provided below.

    # Create the HTML file for a specific game
    game_title = game_data.get('title', 'Unknown Title')
    safe_game_title = sanitize_filename(game_title)
    html_dir = os.path.join('cheat_code', safe_game_title)
    os.makedirs(html_dir, exist_ok=True)

    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{game_title} - Switch Cheats</title>
        <!-- Include Bootstrap CSS and DataTables CSS via CDN -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; margin-bottom: 30px; text-align: center; }}
            .table-container {{ margin-top: 20px; }}
            .cheat-code {{ white-space: pre-wrap; font-family: monospace; background-color: #f8f9fa; padding: 10px; border-radius: 5px; }}
            .header, .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .header {{ margin-bottom: 30px; }}
            .footer {{ margin-top: 30px; }}
            .download-button {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{game_title}</h1>
            <!-- Banner placement -->
        </div>
    '''.format(game_title=game_title)

    html_content += '''
    <div class="container-fluid">
    '''

    # Game details
    game_id = game_data.get('id', 'Unknown ID')
    release_date = game_data.get('release_date', 'Unknown')
    size = game_data.get('size', 'Unknown')
    publisher = game_data.get('publisher', 'Unknown')

    html_content += f'''
    <p><strong>Game ID:</strong> {game_id}<br>
    <strong>Release Date:</strong> {release_date}<br>
    <strong>Size:</strong> {size}<br>
    <strong>Publisher:</strong> {publisher}</p>
    '''

    html_content += '''
    <table id="cheatsTable" class="table table-striped table-bordered" style="width:100%">
        <thead>
            <tr>
                <th>Build ID</th>
                <th>Version</th>
                <th>Source</th>
                <th>Cheat Name</th>
                <th>Codes</th>
                <th>Downloads</th>
            </tr>
        </thead>
        <tbody>
    '''

    build_ids = game_data.get('build_ids', [])
    for build in build_ids:
        build_id = build.get('build_id', 'Unknown Build ID')
        version = build.get('version', 'Unknown Version')
        sources = ', '.join(build.get('sources', []))
        cheat_directory = build.get('cheat_directory', '')
        zip_file = build.get('zip_file', '')

        cheats = build.get('cheats', [])
        if cheats:
            for cheat in cheats:
                cheat_name = cheat.get('name', 'Unknown Cheat')
                date_added = cheat.get('date_added', 'Unknown Date')
                source = cheat.get('source', 'Unknown Source')
                codes_list = cheat.get('codes', [])
                # Format the codes as per your requirement
                codes_formatted = f"[{cheat_name}]\n" + '\n'.join(codes_list)
                codes_html = f'<div class="cheat-code">{codes_formatted}</div>'

                # Create links for cheat directory and zip file
                cheat_dir_link = ''
                zip_file_link = ''
                if cheat_directory:
                    relative_cheat_dir = os.path.relpath(cheat_directory, start=html_dir)
                    cheat_dir_link = f'<a href="{quote(relative_cheat_dir)}">Cheat Directory</a>'
                if zip_file:
                    relative_zip_file = os.path.relpath(zip_file, start=html_dir)
                    zip_file_link = f'<a class="btn btn-primary btn-sm download-button" href="{quote(relative_zip_file)}">Download Zip</a>'

                # Combine links
                links = f'{cheat_dir_link}<br>{zip_file_link}'

                html_content += f'''
                <tr>
                    <td>{build_id}</td>
                    <td>{version}</td>
                    <td>{sources}</td>
                    <td>{cheat_name}</td>
                    <td>{codes_html}</td>
                    <td>{links}</td>
                </tr>
                '''

    html_content += '''
        </tbody>
    </table>
    </div>
    '''

    html_content += '''
        <div class="footer">
            <!-- Footer content -->
            <p>&copy; 2023 Switch Cheats</p>
        </div>
        <!-- Include jQuery, Bootstrap JS, and DataTables JS via CDN -->
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
        <script>
            $(document).ready(function() {{
                var table = $('#cheatsTable').DataTable({{
                    "order": [],
                    "autoWidth": false,
                    "columns": [
                        {{ "width": "15%" }},
                        {{ "width": "10%" }},
                        {{ "width": "10%" }},
                        {{ "width": "20%" }},
                        {{ "width": "35%" }},
                        {{ "width": "10%" }}
                    ]
                }});

                // Add dropdown filters
                $('#cheatsTable thead tr').clone(true).appendTo('#cheatsTable thead');
                $('#cheatsTable thead tr:eq(1) th').each(function (i) {{
                    var title = $(this).text();
                    if (title == 'Build ID' || title == 'Version' || title == 'Source') {{
                        $(this).html('<select class="form-select form-select-sm"><option value="">All</option></select>');
                        table.column(i).data().unique().sort().each(function (d, j) {{
                            $('#cheatsTable thead tr:eq(1) th').eq(i).find('select').append('<option value="'+d+'">'+d+'</option>')
                        }});
                        $('select', this).on('change', function () {{
                            var val = $.fn.dataTable.util.escapeRegex($(this).val());
                            table.column(i).search(val ? '^'+val+'$' : '', true, false).draw();
                        }});
                    }} else {{
                        $(this).html('');
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    '''

    # Save the HTML content to a file inside 'cheat_code/<game_title>' directory
    html_file_path = os.path.join(html_dir, 'index.html')
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logging.info(Fore.GREEN + f"HTML file generated for '{game_title}' at: {html_file_path}")

def generate_main_index_html(game_list):
    # Generate the main index.html that lists all games
    html_dir = 'cheat_code'
    os.makedirs(html_dir, exist_ok=True)

    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title> Switch Cheats</title>
        <!-- Include Bootstrap CSS and DataTables CSS via CDN -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; margin-bottom: 30px; text-align: center; }}
            .table-container {{ margin-top: 20px; }}
            .header, .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
            .header {{ margin-bottom: 30px; }}
            .footer {{ margin-top: 30px; }}
            .download-button {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1> Switch Cheats</h1>
            <!-- Banner placement -->
        </div>
        <div class="container-fluid">
            <table id="gamesTable" class="table table-striped table-bordered" style="width:100%">
                <thead>
                    <tr>
                        <th>Game Title</th>
                        <th>Build ID</th>
                        <th>Version</th>
                        <th>Source</th>
                        <th>Cheats Link</th>
                        <th>Cheat Count</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for game in game_list:
        game_title = game.get('title', 'Unknown Title')
        safe_game_title = sanitize_filename(game_title)
        game_link = f"{quote(safe_game_title)}/index.html"

        for build in game.get('build_ids', []):
            cheat_count = len(build.get('cheats', []))
            if cheat_count == 0:
                continue  # Skip build IDs with zero cheat count

            build_id = build.get('build_id', '')
            version = build.get('version', 'Unknown Version')
            zip_file = build.get('zip_file', '')
            sources = ', '.join(build.get('sources', []))

            if zip_file:
                relative_zip_file = os.path.relpath(zip_file, start=html_dir)
                download_link = f'<a class="btn btn-primary btn-sm download-button" href="{quote(relative_zip_file)}">Download</a>'
            else:
                download_link = 'No Download'

            html_content += f'''
            <tr>
                <td><a href="{game_link}">{game_title}</a></td>
                <td>{build_id}</td>
                <td>{version}</td>
                <td>{sources}</td>
                <td>{download_link}</td>
                <td>{cheat_count}</td>
            </tr>
            '''

    html_content += '''
                </tbody>
            </table>
        </div>
        <div class="footer">
            <!-- Footer content -->
            <p>&copy; 2023 Switch Cheats</p>
        </div>
        <!-- Include jQuery, Bootstrap JS, and DataTables JS via CDN -->
        <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
        <script>
            $(document).ready(function() {{
                var table = $('#gamesTable').DataTable({{
                    "order": [],
                    "autoWidth": false,
                    "columns": [
                        {{ "width": "25%" }},
                        {{ "width": "20%" }},
                        {{ "width": "10%" }},
                        {{ "width": "15%" }},
                        {{ "width": "15%" }},
                        {{ "width": "10%" }}
                    ]
                }});

                // Add dropdown filters
                $('#gamesTable thead tr').clone(true).appendTo('#gamesTable thead');
                $('#gamesTable thead tr:eq(1) th').each(function (i) {{
                    var title = $(this).text();
                    if (title == 'Game Title' || title == 'Build ID' || title == 'Version' || title == 'Source') {{
                        $(this).html('<select class="form-select form-select-sm"><option value="">All</option></select>');
                        table.column(i).data().unique().sort().each(function (d, j) {{
                            $('#gamesTable thead tr:eq(1) th').eq(i).find('select').append('<option value="'+d+'">'+d+'</option>')
                        }});
                        $('select', this).on('change', function () {{
                            var val = $.fn.dataTable.util.escapeRegex($(this).val());
                            table.column(i).search(val ? '^'+val+'$' : '', true, false).draw();
                        }});
                    }} else {{
                        $(this).html('');
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    '''

    # Save the main index.html inside 'cheat_code' directory
    html_file_path = os.path.join(html_dir, 'index.html')
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logging.info(Fore.GREEN + f"Main index HTML file generated at: {html_file_path}")

    # Try to open the main index.html in the default web browser
    try:
        browser = webbrowser.get()
        browser.open(f'file://{os.path.abspath(html_file_path)}')
    except webbrowser.Error:
        logging.info("No web browser found. Skipping opening the web page.")
    except Exception as e:
        logging.warning(Fore.YELLOW + f"Could not open the web browser: {e}")
