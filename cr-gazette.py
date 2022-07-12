import os
from datetime import date
import requests
import bs4


# Date
today_ymd = str(date.today())
year, month, day = today_ymd.split('-')
today = f'{day}-{month}-{year}'
print(f'Working on {today}')

# Root directory
root_directory = '/usr/src/app/downloads/'
download_directory = f'{root_directory}{today}/'

# Check that the issue has not been previously downloaded
if os.path.isdir(download_directory):
    print(f'{download_directory} already exists')

elif not os.path.isdir(download_directory):
    try:
        # PDF viewer -> bytes
        pdf_viewer = requests.get(f'https://www.imprentanacional.go.cr/pub/{year}/{month}/{day}/COMP_{day}_{month}_{year}.pdf')
        print(f'{pdf_viewer}: https://www.imprentanacional.go.cr/pub/{year}/{month}/{day}/COMP_{day}_{month}_{year}.pdf')

        # If given date is valid -> response 200
        if pdf_viewer.status_code == 200:
            # Create download folder
            os.mkdir(f'{root_directory}{today}')
            print(f'Working directory is {download_directory}')

            # Download PDF file
            with open(f'{download_directory}COMP_{day}_{month}_{year}.pdf', 'wb') as pdf_file:
                pdf_file.write(pdf_viewer.content)
                print(f'PDF file downloaded: {download_directory}COMP_{day}_{month}_{year}.pdf')

            # Return HTML for contenido completo 
            seed_url = f'https://www.imprentanacional.go.cr/gaceta/?date={today}'
            html_viewer = requests.get(seed_url)
            print(f'{html_viewer}: {seed_url}')

            # Write contenido completo to a single HTML file
            with open(f'{download_directory}{today}.html', 'w') as contenido_completo:
                contenido_completo.write(html_viewer.text)
                print(f'HTML file downloaded: {download_directory}{today}.html')


            # Split contenido completo into secciones (e.g. Poder Legislativo, etc.)
            contenido_completo_content = open(f'{download_directory}{today}.html', 'r').read()
            secciones = contenido_completo_content.split('<h1>')

            # remove 0 index element (is empty)
            secciones.pop(0) # Is HTML content before first H1 tag

            for index, seccion in enumerate(secciones):
                with open(f'{download_directory}{index}.html', 'w') as n_file:
                    # Add missing <h1> tag since split() method in var secciones removes it
                    n_file.write(f'<h1>{seccion}')

            for html_file in os.listdir(f'{download_directory}'):
                if html_file.endswith('html') and html_file is not f'{today}.html':
                    with open(f'{download_directory}{html_file}') as seccion_content:
                        seccion_str = seccion_content.read()
                        so = bs4.BeautifulSoup(seccion_str, 'html.parser')

                        seccion_name = so.find('h1').text.replace('\n', ' ').strip()
                        os.rename(f'{download_directory}{html_file}', f'{download_directory}{seccion_name}.html')
                        print(f'{download_directory}{seccion_name}.html')

            # Remove portada
            if 'PORTADA.html' in os.listdir(download_directory):
                os.remove(f'{download_directory}PORTADA.html')

    except:
        print(pdf_viewer)
        print(f'DATE HAS NO CONTENT: {today}')
        print(f'PDF: https://www.imprentanacional.go.cr/pub/{year}/{month}/{day}/COMP_{day}_{month}_{year}.pdf')
        print(f'HTML: https://www.imprentanacional.go.cr/gaceta/?date={today}')

else:
    print('An error occurred, please check the following:')
    print(f'PDF: https://www.imprentanacional.go.cr/pub/{year}/{month}/{day}/COMP_{day}_{month}_{year}.pdf')
    print(f'HTML: https://www.imprentanacional.go.cr/gaceta/?date={today}')
